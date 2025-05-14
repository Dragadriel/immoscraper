FROM python:3.9-slim

WORKDIR /app

# Systemabhängigkeiten installieren
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Kopiere Anforderungen und installiere sie
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere den Quellcode
COPY *.py .
# Erstelle Datenverzeichnis
RUN mkdir -p /app/data

# Umgebungsvariablen setzen
ENV CACHE_FILE="/app/data/seen_listings.txt"

# Setze den Eintragspunkt
CMD ["python", "main.py"]
