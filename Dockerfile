# Usa una immagine base leggera per Python
FROM python:3.9-slim

# Imposta la directory di lavoro
WORKDIR /app

# Copia il file requirements.txt e installa le dipendenze
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia il resto del codice nel container
COPY . .

# Espone la porta su cui Flask gira (predefinita 5000)
EXPOSE 5000

# Comando di avvio
CMD ["python3", "app.py"]