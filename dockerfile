FROM python:3.10-slim

# Arbeitsverzeichnis erstellen
WORKDIR /app

# Abhängigkeiten installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Anwendungscode kopieren
COPY wbm_scraper.py .

# Umgebungsvariablen setzen (diese werden in Railway überschrieben)
ENV TELEGRAM_TOKEN=""
ENV TELEGRAM_CHAT_ID=""
ENV MIN_ROOMS="1"
ENV MAX_ROOMS="5"
ENV MIN_AREA="20"
ENV MAX_AREA="200"
ENV MAX_RENT="2000"
ENV MAX_PRICE_PER_SQM="20"
ENV DISTRICTS=""
ENV SCHEDULE_MINUTES="5"
ENV SCHEDULE_START_HOUR="8"
ENV SCHEDULE_END_HOUR="23"
ENV SCHEDULE_DAYS="mon-sun"
ENV DATA_FILE="wohnungen.json"

# Anwendung starten
CMD ["python", "wbm_scraper.py"]
