# Verwende das vorgefertigte Playwright-Image
FROM mcr.microsoft.com/playwright/python:v1.43.0-jammy

# Setze Arbeitsverzeichnis
WORKDIR /app

# Kopiere Projektdateien
COPY . .

# Installiere Python-Abhängigkeiten
RUN pip install --no-cache-dir -r requirements.txt

# Installiere die Playwright-Browser (zwingend notwendig!)
RUN playwright install --with-deps

# Starte das Skript
CMD ["python", "main.py"]
