import os
import time
import requests
import logging
import schedule
import threading
from datetime import datetime
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import random

# Logger konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("immoscraper")

# Lade Umgebungsvariablen
load_dotenv()

# Konstanten
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SEARCH_URL = os.getenv("SEARCH_URL")

# Liste bereits gesehener Inserate (In-Memory Cache)
seen_listings = set()
# Datei für persistenten Cache
CACHE_FILE = "seen_listings.txt"

# Liste von Begriffen, die ausgeschlossen werden sollen
# Diese könnten auch in einer separaten Datei gespeichert werden
FILTER_WORDS = [
    "wg", "untermiete", "zwischenmiete", "befristet", "tausch",
    "wohnung auf zeit", "möbliert", "möblierte", "studenten",
    "wohngemeinschaft"
]

# User-Agent Liste für zufällige Auswahl
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
]

def load_seen_listings():
    """Lädt bereits gesehene Inserate aus der Datei"""
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r") as f:
                for line in f:
                    seen_listings.add(line.strip())
            logger.info(f"Geladen: {len(seen_listings)} bekannte Inserate")
    except Exception as e:
        logger.error(f"Fehler beim Laden der bekannten Inserate: {e}")

def save_listing_to_cache(listing_id):
    """Speichert ein Inserat in der Cache-Datei"""
    try:
        with open(CACHE_FILE, "a") as f:
            f.write(f"{listing_id}\n")
    except Exception as e:
        logger.error(f"Fehler beim Speichern des Inserats {listing_id}: {e}")

def should_filter(title, description):
    """Prüft, ob ein Inserat gefiltert werden soll"""
    text = (title + " " + description).lower()
    for word in FILTER_WORDS:
        if word.lower() in text:
            return True
    return False

def send_telegram_message(message):
    """Sendet eine Nachricht über Telegram"""
    if not TELEGRAM_TOKEN or not CHAT_ID:
        logger.error("Telegram-Konfiguration fehlt. Nachricht wird nicht gesendet.")
        return
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, data=data)
        if response.status_code != 200:
            logger.error(f"Fehler beim Senden der Telegram-Nachricht: {response.text}")
        else:
            logger.info("Telegram-Nachricht erfolgreich gesendet")
    except Exception as e:
        logger.error(f"Fehler beim Senden der Telegram-Nachricht: {e}")

def scrape_immoscout():
    """Scrapt ImmoScout24 nach neuen Wohnungsangeboten"""
    logger.info(f"Starte Scraping von {SEARCH_URL}")
    
    if not SEARCH_URL:
        logger.error("Keine Such-URL konfiguriert")
        return
    
    # Headers mit zufälligem User-Agent
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0"
    }
    
    try:
        # Füge zufällige Verzögerung hinzu, um natürliches Verhalten zu simulieren
        time.sleep(random.uniform(1, 3))
        
        # Anfrage senden
        response = requests.get(SEARCH_URL, headers=headers, timeout=30)
        
        # Status prüfen
        if response.status_code != 200:
            logger.error(f"Fehler beim Abrufen der Seite: Status {response.status_code}")
            return
        
        # Debug-Information
        logger.debug(f"HTML-Größe: {len(response.text)} Bytes")
        
        # HTML parsen
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Alle Resultate finden
        # Angepasst an aktuelle ImmoScout24-Struktur (Mai 2025)
        # Hier müsste die aktuelle Struktur der Seite analysiert werden
        results = soup.select("ol.result-list__listing > li")
        
        # Alternativ können wir noch weitere Selektoren probieren, wenn die obige nicht funktioniert
        if not results:
            results = soup.select("ul#resultListItems li.result-list__listing")
        
        # Noch eine weitere Alternative
        if not results:
            results = soup.select("div[data-testid='result-list-entry']")
        
        logger.info(f"Gefundene Inserate: {len(results)}")
        
        # Wenn keine Ergebnisse gefunden wurden, speichere HTML zur Analyse
        if not results:
            with open("debug_response.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            logger.warning("Keine Inserate gefunden. HTML wurde zur Analyse gespeichert.")
            return
        
        new_listings = 0
        
        # Ergebnisse verarbeiten
        for result in results:
            try:
                # ID des Inserats extrahieren
                # ID kann in verschiedenen Attributen gespeichert sein
                listing_id = None
                if result.get("data-id"):
                    listing_id = result.get("data-id")
                elif result.get("id"):
                    listing_id = result.get("id")
                elif result.get("data-listing-id"):
                    listing_id = result.get("data-listing-id")
                
                # Wenn keine ID gefunden wurde, mit dem nächsten Ergebnis fortfahren
                if not listing_id:
                    logger.warning("ID für ein Inserat konnte nicht extrahiert werden")
                    continue
                
                # Prüfen, ob dieses Inserat bereits gesehen wurde
                if listing_id in seen_listings:
                    continue
                
                # Link extrahieren
                link_elem = result.select_one("a[href*='/expose/']")
                if not link_elem:
                    logger.warning(f"Link für Inserat {listing_id} nicht gefunden")
                    continue
                
                link = link_elem.get("href")
                if not link.startswith("http"):
                    link = "https://www.immobilienscout24.de" + link
                
                # Titel und Beschreibung extrahieren
                title_elem = result.select_one("h5") or result.select_one("h2") or result.select_one("[data-testid='result-list-entry-headline']")
                title = title_elem.text.strip() if title_elem else "Kein Titel"
                
                description_elem = result.select_one("p") or result.select_one("[data-testid='result-list-entry-description']")
                description = description_elem.text.strip() if description_elem else ""
                
                # Preis extrahieren
                price_elem = result.select_one("[data-testid='result-list-entry-primary-criteria'] span:first-child") or result.select_one(".result-list-entry__primary-criterion:first-child")
                price = price_elem.text.strip() if price_elem else "Preis nicht angegeben"
                
                # Größe extrahieren
                size_elem = result.select_one("[data-testid='result-list-entry-primary-criteria'] span:nth-child(2)") or result.select_one(".result-list-entry__primary-criterion:nth-child(2)")
                size = size_elem.text.strip() if size_elem else "Größe nicht angegeben"
                
                # Filtern der Inserate
                if should_filter(title, description):
                    logger.info(f"Inserat {listing_id} wurde aufgrund von Filterkriterien übersprungen")
                    seen_listings.add(listing_id)
                    save_listing_to_cache(listing_id)
                    continue
                
                # Nachricht erstellen
                message = f"*Neues Inserat!*\n\n"
                message += f"*{title}*\n"
                message += f"Preis: {price}\n"
                message += f"Größe: {size}\n\n"
                if description:
                    message += f"{description}\n\n"
                message += f"[Zum Inserat]({link})"
                
                # Nachricht senden
                send_telegram_message(message)
                
                # Inserat als gesehen markieren
                seen_listings.add(listing_id)
                save_listing_to_cache(listing_id)
                
                new_listings += 1
                
            except Exception as e:
                logger.error(f"Fehler bei der Verarbeitung eines Inserats: {e}")
        
        logger.info(f"Verarbeitung abgeschlossen. {new_listings} neue Inserate gefunden.")
        
    except requests.RequestException as e:
        logger.error(f"Anfragefehler: {e}")
    except Exception as e:
        logger.error(f"Unerwarteter Fehler: {e}")

def job():
    """Hauptfunktion, die regelmäßig ausgeführt wird"""
    try:
        current_time = datetime.now().strftime("%H:%M:%S")
        logger.info(f"Job gestartet um {current_time}")
        scrape_immoscout()
    except Exception as e:
        logger.error(f"Fehler im Job: {e}")

def run_threaded(job_func):
    """Führt eine Funktion in einem eigenen Thread aus"""
    job_thread = threading.Thread(target=job_func)
    job_thread.start()

def main():
    """Hauptfunktion"""
    try:
        logger.info("ImmoScraper gestartet")
        
        # Lade bekannte Inserate
        load_seen_listings()
        
        # Zeitplan einrichten
        schedule.every(5).minutes.do(run_threaded, job)
        
        # Job einmal sofort ausführen
        job()
        
        # Endlosschleife
        while True:
            schedule.run_pending()
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("ImmoScraper wird beendet")
    except Exception as e:
        logger.error(f"Unerwarteter Fehler: {e}")
        
if __name__ == "__main__":
    main()
