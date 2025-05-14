# ImmoScraper

Ein Python-Tool, um automatisch Wohnungsangebote von ImmoScout24 zu überwachen und über Telegram zu benachrichtigen.

## Features

- Regelmäßiges Scraping von ImmoScout24-Suchergebnissen
- Benachrichtigung über neue Wohnungsangebote via Telegram
- Filterung von unerwünschten Angeboten (WG, Untermiete, befristete Angebote, etc.)
- Cache zur Vermeidung doppelter Benachrichtigungen
- Docker-Unterstützung für einfache Bereitstellung

## Installation und Einrichtung

### Voraussetzungen
- Python 3.7+
- Ein Telegram-Bot-Token ([BotFather](https://t.me/botfather) verwenden)
- Eine Telegram-Chat-ID (kann über [@userinfobot](https://t.me/userinfobot) ermittelt werden)

### Lokale Installation

1. Repository klonen:
   ```
   git clone https://github.com/dein-username/immoscraper.git
   cd immoscraper
   ```

2. Virtuelle Umgebung erstellen und aktivieren:
   ```
   python -m venv venv
   source venv/bin/activate  # Unter Windows: venv\Scripts\activate
   ```

3. Abhängigkeiten installieren:
   ```
   pip install -r requirements.txt
   ```

4. Konfigurationsdatei erstellen:
   ```
   cp .env.template .env
   ```

5. `.env`-Datei bearbeiten und die erforderlichen Werte eintragen:
   - `TELEGRAM_TOKEN`: Das Token deines Telegram-Bots
   - `CHAT_ID`: Die Chat-ID deines Telegram-Chats
   - `SEARCH_URL`: Der ImmoScout24-Suchlink mit deinen Filterkriterien

### Docker-Installation

1. Repository klonen:
   ```
   git clone https://github.com/dein-username/immoscraper.git
   cd immoscraper
   ```

2. Konfigurationsdatei erstellen:
   ```
   cp .env.template .env
   ```

3. `.env`-Datei bearbeiten und die erforderlichen Werte eintragen

4. Mit Docker Compose starten:
   ```
   docker-compose up -d
   ```

## Deployment auf Railway

1. Fork dieses Repository auf GitHub

2. Melde dich bei [Railway](https://railway.app/) an und erstelle ein neues Projekt

3. Wähle "Deploy from GitHub repo" und verbinde dein Repository

4. Setze die Umgebungsvariablen in Railway:
   - `TELEGRAM_TOKEN`: Das Token deines Telegram-Bots
   - `CHAT_ID`: Die Chat-ID deines Telegram-Chats
   - `SEARCH_URL`: Der ImmoScout24-Suchlink mit deinen Filterkriterien
   - `SCRAPING_START_HOUR`: Beginn des Scraping-Zeitfensters (Standard: 8)
   - `SCRAPING_END_HOUR`: Ende des Scraping-Zeitfensters (Standard: 23)
   - `SCRAPING_DAYS`: Tage für das Scraping (Standard: 0,1,2,3,4 = Mo-Fr)
   - `SCRAPING_INTERVAL`: Intervall in Minuten (Standard: 5)

5. Starte den Deploy

## Erweiterte Anpassung

### Zeitfenster für das Scraping

Das Scraping kann auf bestimmte Stunden und Wochentage beschränkt werden:

- `SCRAPING_START_HOUR`: Beginn des Scraping-Zeitfensters (Stunde, 0-23), Standard: 8
- `SCRAPING_END_HOUR`: Ende des Scraping-Zeitfensters (Stunde, 0-23), Standard: 23
- `SCRAPING_DAYS`: Tage für das Scraping als kommagetrennte Liste (0=Mo, 1=Di, ..., 6=So), Standard: 0,1,2,3,4 (Mo-Fr)
- `SCRAPING_INTERVAL`: Intervall in Minuten zwischen Scraping-Jobs, Standard: 5

Diese Werte können in der `.env`-Datei oder direkt als Umgebungsvariablen in Railway gesetzt werden.

### Filterworte anpassen

Die Filterworte können im Code unter `FILTER_WORDS` angepasst werden:

```python
FILTER_WORDS = [
    "wg", "untermiete", "zwischenmiete", "befristet", "tausch",
    "wohnung auf zeit", "möbliert", "möblierte", "studenten",
    "wohngemeinschaft"
]
```

### Scraping-Intervall ändern

Das Standard-Intervall für das Scraping beträgt 5 Minuten. Dieses kann im Code geändert werden:

```python
# Zeitplan einrichten (von 5 Minuten auf z.B. 10 Minuten ändern)
schedule.every(10).minutes.do(run_threaded, job)
```

## Fehlersuche

Bei Problemen können folgende Schritte helfen:

1. Prüfe die Log-Datei `app.log`
2. Stelle sicher, dass die Umgebungsvariablen korrekt gesetzt sind
3. Überprüfe, ob der Telegram-Bot korrekt eingerichtet ist
4. Prüfe, ob dein Suchlink gültig ist und Ergebnisse liefert

Die Datei `debug_response.html` wird erstellt, wenn keine Suchergebnisse gefunden werden. Diese kann zur Analyse der HTML-Struktur verwendet werden.

## Hinweise

- ImmoScout24 kann seine HTML-Struktur ändern, was ein Update der Scraper-Logik erfordern kann
- Übermäßiges Scraping kann zu einer Blockierung deiner IP-Adresse führen
- Dieses Tool ist nur für den persönlichen Gebrauch gedacht und sollte verantwortungsvoll eingesetzt werden
