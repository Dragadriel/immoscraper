# Basisimage
FROM mcr.microsoft.com/playwright/python:v1.43.0-jammy

# Set Arbeitsverzeichnis
WORKDIR /app

# Kopiere Projektdateien
COPY . /app

# Installiere Python-Abhängigkeiten
RUN pip install --no-cache-dir -r requirements.txt

# (optional) Debug: Zeige installierte Browser
RUN ls -la /ms-playwright

# Setze Umgebungsvariable – zwinge Playwright, installierte Browser zu nutzen
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Standardbefehl
CMD ["python", "main.py"]
