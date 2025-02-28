import os
from flask import Flask, render_template, request, redirect, flash, send_file
from werkzeug.utils import secure_filename
import pandas as pd

app = Flask(__name__)
app.secret_key = 'super-secret-key'  # Cambia con una chiave sicura

# Directory per salvare i file caricati e l'output
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

def allowed_file(filename):
    """Controlla l'estensione del file."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Recupera i file e le colonne da confrontare
        file1 = request.files.get('file1')
        file2 = request.files.get('file2')
        col1_str = request.form.get('col1', '').strip()
        col2_str = request.form.get('col2', '').strip()

        # Validazioni di base
        if not file1 or not file2 or file1.filename == '' or file2.filename == '':
            flash("Seleziona entrambi i file Excel.")
            return redirect(request.url)
        if not col1_str or not col2_str:
            flash("Inserisci i numeri di colonna per entrambi i file.")
            return redirect(request.url)
        if not allowed_file(file1.filename) or not allowed_file(file2.filename):
            flash("I file devono avere estensione .xlsx o .xls")
            return redirect(request.url)

        try:
            col1_idx = int(col1_str) - 1
            col2_idx = int(col2_str) - 1
        except ValueError:
            flash("Devi inserire numeri validi per le colonne.")
            return redirect(request.url)
        if col1_idx < 0 or col2_idx < 0:
            flash("I numeri di colonna devono essere >= 1.")
            return redirect(request.url)

        # Salva i file
        filename1 = secure_filename(file1.filename)
        filename2 = secure_filename(file2.filename)
        path1 = os.path.join(UPLOAD_FOLDER, filename1)
        path2 = os.path.join(UPLOAD_FOLDER, filename2)
        file1.save(path1)
        file2.save(path2)

        # Legge i DataFrame dai file Excel
        try:
            df1 = pd.read_excel(path1, engine='openpyxl')
            df2 = pd.read_excel(path2, engine='openpyxl')
        except Exception as e:
            flash(f"Errore nella lettura dei file Excel: {e}")
            return redirect(request.url)

        # Verifica che le colonne richieste esistano
        if col1_idx >= df1.shape[1]:
            flash(f"Il file {file1.filename} non ha la colonna {col1_idx + 1}")
            return redirect(request.url)
        if col2_idx >= df2.shape[1]:
            flash(f"Il file {file2.filename} non ha la colonna {col2_idx + 1}")
            return redirect(request.url)

        # Confronta i valori: per ogni valore in df1, cerca corrispondenze in df2 (in qualsiasi riga)
        rows = []
        col1_values = df1.iloc[:, col1_idx]
        col2_values = df2.iloc[:, col2_idx]

        for idx, val in col1_values.items():
            val_str = str(val).strip().lower() if pd.notna(val) else ""
            matching_rows = col2_values.apply(lambda x: str(x).strip().lower() if pd.notna(x) else "").eq(val_str)
            matched_indices = matching_rows[matching_rows].index.tolist()

            if matched_indices:
                match = "YES"
                matched_rows_str = ", ".join(str(i + 1) for i in matched_indices)
            else:
                match = "NO"
                matched_rows_str = ""

            rows.append({
                "Row_file1": idx + 1,
                "Value_file1": val,
                "Matching_Rows_in_file2": matched_rows_str,
                "Match": match
            })

        confronto = pd.DataFrame(rows)
        output_path = os.path.join(UPLOAD_FOLDER, "confronto_result.xlsx")
        confronto.to_excel(output_path, index=False)
        return send_file(output_path, as_attachment=True)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)