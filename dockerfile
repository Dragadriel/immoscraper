# Verwende das offizielle Python-Image
FROM python:3.12-slim

# Installiere systemweite Abhängigkeiten für Playwright
RUN apt-get update && apt-get install -y \
    libx11-xcb1 \
    libnss3 \
    libgdk-pixbuf2.0-0 \
    libgbm1 \
    libatk1.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libasound2 \
    libdbus-1-3 \
    libxtst6 \
    libgtk-3-0 \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Installiere Playwright und den benötigten Browser
RUN pip install --no-cache-dir playwright
RUN playwright install --with-deps

# Kopiere die Anwendung in das Container-Verzeichnis
COPY . /app
WORKDIR /app

# Setze Umgebungsvariablen (optional)
# Setze Playwright-Browser-Cache, falls notwendig
ENV PLAYWRIGHT_BROWSERS_PATH=/root/.cache/ms-playwright

# Installiere die benötigten Python-Pakete
RUN pip install -r requirements.txt

# Stelle sicher, dass Playwright die richtigen Berechtigungen hat
RUN chmod -R 777 /root/.cache/ms-playwright

# Starte die Anwendung
CMD ["python", "main.py"]
