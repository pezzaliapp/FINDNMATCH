import os
from flask import Flask, render_template, request, redirect, flash, send_file
from werkzeug.utils import secure_filename
import pandas as pd

app = Flask(__name__)
app.secret_key = 'super-secret-key'  # Cambia con una chiave sicura

# Cartella di lavoro (dove salviamo i file caricati e l'output)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

def allowed_file(filename):
    """Controlla l'estensione."""
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        # 1. Recupera i due file
        file1 = request.files.get('file1')
        file2 = request.files.get('file2')

        # 2. Recupera i numeri di colonna inseriti
        col1_str = request.form.get('col1', '').strip()
        col2_str = request.form.get('col2', '').strip()

        # Controlli di base
        if not file1 or not file2 or file1.filename == '' or file2.filename == '':
            flash("Seleziona entrambi i file Excel.")
            return redirect(request.url)

        if not col1_str or not col2_str:
            flash("Inserisci i numeri di colonna per entrambi i file.")
            return redirect(request.url)

        if not allowed_file(file1.filename) or not allowed_file(file2.filename):
            flash("I file devono avere estensione .xlsx o .xls")
            return redirect(request.url)

        # Converte i numeri di colonna da 1-based a 0-based
        try:
            col1_idx = int(col1_str) - 1
            col2_idx = int(col2_str) - 1
        except ValueError:
            flash("Devi inserire numeri validi per le colonne.")
            return redirect(request.url)

        if col1_idx < 0 or col2_idx < 0:
            flash("I numeri di colonna devono essere >= 1.")
            return redirect(request.url)

        # 3. Salva i file
        filename1 = secure_filename(file1.filename)
        filename2 = secure_filename(file2.filename)
        path1 = os.path.join(UPLOAD_FOLDER, filename1)
        path2 = os.path.join(UPLOAD_FOLDER, filename2)
        file1.save(path1)
        file2.save(path2)

        # 4. Leggi i due DataFrame
        try:
            df1 = pd.read_excel(path1, engine='openpyxl')
            df2 = pd.read_excel(path2, engine='openpyxl')
        except Exception as e:
            flash(f"Errore nel leggere i file Excel: {e}")
            return redirect(request.url)

        # 5. Determina il numero massimo di righe
        max_rows = max(len(df1), len(df2))

        # Creiamo un nuovo DataFrame di confronto
        # con 3 colonne: "valore_file1", "valore_file2", "Match"
        confronto = pd.DataFrame(columns=['valore_file1','valore_file2','Match'])

        for i in range(max_rows):
            if i < len(df1) and col1_idx < df1.shape[1]:
                val1 = df1.iloc[i, col1_idx]
            else:
                val1 = float('nan')  # riga o colonna non esistente

            if i < len(df2) and col2_idx < df2.shape[1]:
                val2 = df2.iloc[i, col2_idx]
            else:
                val2 = float('nan')

            # Normalizziamo per confrontare ignorando spazi / maiuscole
            s1 = str(val1).strip().lower() if pd.notna(val1) else None
            s2 = str(val2).strip().lower() if pd.notna(val2) else None

            if s1 is None or s2 is None:
                match = "NO"
            else:
                match = "YES" if (s1 == s2) else "NO"

            confronto.loc[i] = [val1, val2, match]

        # 6. Salviamo il risultato
        output_path = os.path.join(UPLOAD_FOLDER, "confronto_result.xlsx")
        confronto.to_excel(output_path, index=False)

        return send_file(output_path, as_attachment=True)

    # GET
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)