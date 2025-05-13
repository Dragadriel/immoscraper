# Verwende ein Python-Image als Basis
FROM python:3.12-slim

# Installiere die notwendigen System-Pakete für Chromium und Playwright
RUN apt-get update && \
    apt-get install -y \
    libnss3 \
    libatk-1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libx11-6 \
    libxcomposite1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libxfixes3 \
    libdbus-1-3 \
    libpango-1.0-0 \
    libatk1.0-0 \
    libxkbcommon0 \
    libxdamage1 \
    libnspr4 \
    libatspi2.0-0 \
    libcairo2 \
    libxcb1 \
    && apt-get clean

# Installiere Playwright und seine Abhängigkeiten
RUN pip install --no-cache-dir playwright==1.44.0
RUN playwright install

# Setze das Arbeitsverzeichnis
WORKDIR /app

# Kopiere den Code ins Container-Verzeichnis
COPY . /app

# Installiere die Python-Abhängigkeiten
RUN pip install -r requirements.txt

# Stelle sicher, dass das Skript ausführbar ist
RUN chmod +x start.sh

# Führe das Startskript aus
CMD ["bash", "start.sh"]
