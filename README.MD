WBM Wohnungsangebot-Scraper mit Telegram-Benachrichtigung

Ein automatisiertes Tool zum Scrapen von Wohnungsangeboten der WBM Berlin mit Telegram-Benachrichtigungen.
Funktionen

    Regelmäßiges Scraping der WBM-Website nach Wohnungsangeboten
    Filterung nach benutzerdefinierten Kriterien (Zimmeranzahl, Fläche, Preis, Bezirk)
    Telegram-Benachrichtigungen bei neuen passenden Angeboten
    Vermeidung von Duplikaten durch Speicherung bereits gefundener Wohnungen
    Anpassbarer Zeitplan (z.B. alle 5 Minuten von Mo-Fr, 8:00 bis 23:00 Uhr)
    Einfaches Deployment in der kostenlosen Version von Railway.app

Lokale Einrichtung für Tests

    Repository klonen
    Python-Umgebung einrichten
    Abhängigkeiten installieren: pip install -r requirements.txt
    Erstellen Sie einen Telegram-Bot und notieren Sie den Token (siehe Anleitung unten)
    Konfigurationsparameter als Umgebungsvariablen setzen oder in einer .env-Datei speichern
    Starten Sie das Skript: python wbm_scraper.py

Telegram-Bot einrichten

    Öffnen Sie den Telegram-Messenger
    Suchen Sie nach "@BotFather" und starten Sie eine Konversation
    Senden Sie /newbot und folgen Sie den Anweisungen
    Speichern Sie den generierten Bot-Token für die Konfiguration
    Starten Sie eine Konversation mit Ihrem neuen Bot
    Herausfinden Ihrer Chat-ID:
        Öffnen Sie https://api.telegram.org/bot[IHR_TOKEN]/getUpdates
        Schicken Sie eine Nachricht an Ihren Bot
        Aktualisieren Sie die URL und suchen Sie nach "id":123456789 in der JSON-Antwort

Konfigurationsparameter

Parameter	Beschreibung	Standardwert
TELEGRAM_TOKEN	Token Ihres Telegram-Bots	""
TELEGRAM_CHAT_ID	Ihre Telegram-Chat-ID	""
MIN_ROOMS	Minimale Anzahl an Zimmern	1
MAX_ROOMS	Maximale Anzahl an Zimmern	5
MIN_AREA	Minimale Wohnfläche in m²	20
MAX_AREA	Maximale Wohnfläche in m²	200
MAX_RENT	Maximale Warmmiete in €	2000
MAX_PRICE_PER_SQM	Maximaler Preis pro m² in €	20
DISTRICTS	Kommagetrennte Liste von Bezirken	"" (alle)
SCHEDULE_MINUTES	Intervall in Minuten	5
SCHEDULE_START_HOUR	Startzeit (Stunde)	8
SCHEDULE_END_HOUR	Endzeit (Stunde)	23
SCHEDULE_DAYS	Wochentage (mon-sun, mon-fri oder mon,tue,wed,thu,fri)	mon-sun
DATA_FILE	Dateiname für die Speicherung bekannter Wohnungen	wohnungen.json

Bezirke in Berlin

Verfügbare Bezirke für den DISTRICTS-Parameter:

    charlottenburg (umfasst auch Wilmersdorf)
    friedrichshain (umfasst auch Kreuzberg)
    lichtenberg
    marzahn (umfasst auch Hellersdorf)
    mitte
    neukölln
    pankow (umfasst auch Prenzlauer Berg, Weißensee)
    reinickendorf
    spandau
    steglitz (umfasst auch Zehlendorf)
    tempelhof (umfasst auch Schöneberg)
    treptow (umfasst auch Köpenick)

Deployment auf Railway.app

    Erstellen Sie ein Konto auf Railway.app
    Erstellen Sie ein neues Projekt und wählen Sie "Deploy from GitHub repo"
    Verbinden Sie Ihr GitHub-Konto und wählen Sie das Repository aus
    Stellen Sie die Umgebungsvariablen in den Railway-Projekteinstellungen ein
    Railway wird das Projekt automatisch bauen und starten

Wichtige Railway.app Einstellungen

    Stellen Sie sicher, dass Sie im kostenlosen Tarif bleiben (500 Stunden pro Monat)
    Aktivieren Sie die Option "Always On", damit der Scraper kontinuierlich läuft
    Konfigurieren Sie die Umgebungsvariablen in den Projekteinstellungen, insbesondere:
        TELEGRAM_TOKEN
        TELEGRAM_CHAT_ID
        Ihre Filterkriterien (MIN_ROOMS, MAX_RENT usw.)

Beispiele für Filterkriterien
Kleine Wohnung in Kreuzberg oder Neukölln

MIN_ROOMS=1
MAX_ROOMS=2
MIN_AREA=35
MAX_AREA=60
MAX_RENT=800
MAX_PRICE_PER_SQM=15
DISTRICTS=friedrichshain,neukölln

Familiengeeignete Wohnung in ruhigen Gegenden

MIN_ROOMS=3
MAX_ROOMS=5
MIN_AREA=70
MAX_AREA=120
MAX_RENT=1600
MAX_PRICE_PER_SQM=18
DISTRICTS=steglitz,charlottenburg,pankow

Problembehandlung

    Bot sendet keine Nachrichten: Überprüfen Sie den Token und die Chat-ID
    Keine Wohnungen gefunden: Überprüfen Sie Ihre Filterkriterien
    Railway-Deployment schlägt fehl: Überprüfen Sie die Logs und stellen Sie sicher, dass alle Abhängigkeiten korrekt installiert sind

