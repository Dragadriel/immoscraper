import requests
from bs4 import BeautifulSoup
import json
import os
import time
import schedule
import logging
import telegram
from datetime import datetime
import re
import pytz

# Konfiguration der Logging-Funktion
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Konfiguration laden
def load_config():
    """Konfiguration aus Umgebungsvariablen laden"""
    return {
        "telegram_token": os.environ.get("TELEGRAM_TOKEN", ""),
        "telegram_chat_id": os.environ.get("TELEGRAM_CHAT_ID", ""),
        "min_rooms": float(os.environ.get("MIN_ROOMS", 1)),
        "max_rooms": float(os.environ.get("MAX_ROOMS", 5)),
        "min_area": float(os.environ.get("MIN_AREA", 20)),
        "max_area": float(os.environ.get("MAX_AREA", 200)),
        "max_rent": float(os.environ.get("MAX_RENT", 2000)),
        "max_price_per_sqm": float(os.environ.get("MAX_PRICE_PER_SQM", 20)),
        "districts": os.environ.get("DISTRICTS", "").split(","),
        "schedule_minutes": int(os.environ.get("SCHEDULE_MINUTES", 5)),
        "schedule_start_hour": int(os.environ.get("SCHEDULE_START_HOUR", 8)),
        "schedule_end_hour": int(os.environ.get("SCHEDULE_END_HOUR", 23)),
        "schedule_days": os.environ.get("SCHEDULE_DAYS", "mon-sun").lower(),
        "data_file": os.environ.get("DATA_FILE", "wohnungen.json")
    }

# Mapping der Berliner Bezirke für Filter und Normalisierung
BERLIN_DISTRICTS = {
    "charlottenburg": ["charlottenburg", "wilmersdorf", "charlottenburg-wilmersdorf"],
    "friedrichshain": ["friedrichshain", "kreuzberg", "friedrichshain-kreuzberg"],
    "lichtenberg": ["lichtenberg"],
    "marzahn": ["marzahn", "hellersdorf", "marzahn-hellersdorf"],
    "mitte": ["mitte"],
    "neukölln": ["neukölln"],
    "pankow": ["pankow", "prenzlauer berg", "weißensee"],
    "reinickendorf": ["reinickendorf"],
    "spandau": ["spandau"],
    "steglitz": ["steglitz", "zehlendorf", "steglitz-zehlendorf"],
    "tempelhof": ["tempelhof", "schöneberg", "tempelhof-schöneberg"],
    "treptow": ["treptow", "köpenick", "treptow-köpenick"]
}

# Hilfsfunktion zum Normalisieren von Bezirksnamen
def normalize_district(district):
    district = district.lower().strip()
    for main_district, variants in BERLIN_DISTRICTS.items():
        if any(variant in district for variant in variants):
            return main_district
    return district

class WohnungScraper:
    def __init__(self, config):
        self.config = config
        self.bot = telegram.Bot(token=config["telegram_token"])
        self.known_apartments = self.load_known_apartments()
        self.berlin_timezone = pytz.timezone('Europe/Berlin')

    def load_known_apartments(self):
        """Bereits bekannte Wohnungen aus der Datei laden"""
        try:
            if os.path.exists(self.config["data_file"]):
                with open(self.config["data_file"], "r", encoding="utf-8") as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"Fehler beim Laden der bekannten Wohnungen: {e}")
            return []

    def save_known_apartments(self):
        """Bekannte Wohnungen in die Datei speichern"""
        try:
            with open(self.config["data_file"], "w", encoding="utf-8") as f:
                json.dump(self.known_apartments, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Fehler beim Speichern der bekannten Wohnungen: {e}")

    def extract_address_and_district(self, location_text):
        """Extrahiert Adresse und Bezirk aus dem Standorttext"""
        if not location_text:
            return "", ""
        
        address = location_text.strip()
        district = ""
        
        # Versuch, den Bezirk zu extrahieren (typischerweise "Bezirk: XYZ")
        district_match = re.search(r'Bezirk:\s*([^,]+)', location_text, re.IGNORECASE)
        if district_match:
            district = district_match.group(1).strip()
        else:
            # Alternativ: Versuche den Bezirk aus der Adresse zu extrahieren
            parts = location_text.split(',')
            if len(parts) > 1:
                potential_district = parts[-1].strip()
                # Prüfen, ob es ein bekannter Berliner Bezirk ist
                district = normalize_district(potential_district)
        
        return address, district.lower()

    def parse_apartment(self, apartment_div):
        """Extrahiere Informationen aus einem Wohnungs-Div"""
        try:
            # Basis-URL für Detailseiten
            base_url = "https://www.wbm.de"
            
            # Link zur Detailseite
            link_elem = apartment_div.find('a', class_='vacancy-tile__link')
            detail_url = base_url + link_elem['href'] if link_elem and 'href' in link_elem.attrs else ""
            
            # ID aus der URL extrahieren
            apartment_id = detail_url.split('/')[-1] if detail_url else None
            
            # Titel/Überschrift
            title_elem = apartment_div.find('h2', class_='vacancy-tile__title')
            title = title_elem.text.strip() if title_elem else ""
            
            # Adresse/Standort
            location_elem = apartment_div.find('p', class_='vacancy-tile__location')
            location_text = location_elem.text.strip() if location_elem else ""
            address, district = self.extract_address_and_district(location_text)
            
            # Zimmeranzahl
            rooms_elem = apartment_div.select_one('.vacancy-detail:nth-child(1) .vacancy-detail__value')
            rooms_text = rooms_elem.text.strip() if rooms_elem else "0"
            rooms = float(rooms_text.replace(',', '.')) if rooms_text and rooms_text != "-" else 0
            
            # Wohnfläche
            area_elem = apartment_div.select_one('.vacancy-detail:nth-child(2) .vacancy-detail__value')
            area_text = area_elem.text.strip() if area_elem else "0"
            area = float(area_text.split()[0].replace(',', '.')) if area_text and area_text != "-" else 0
            
            # Warmmiete
            rent_elem = apartment_div.select_one('.vacancy-detail:nth-child(3) .vacancy-detail__value')
            rent_text = rent_elem.text.strip() if rent_elem else "0"
            # Entfernen von "€" und konvertieren zu Float
            rent = float(rent_text.replace('€', '').replace('.', '').replace(',', '.').strip()) if rent_text and rent_text != "-" else 0
            
            # Preis pro m²
            sqm_price = rent / area if area > 0 else 0
            
            # Verfügbarkeitsdatum
            available_elem = apartment_div.find('p', class_='vacancy-tile__available')
            available_text = available_elem.text.strip() if available_elem else ""
            available_match = re.search(r'verfügbar ab\s+(\d{2}\.\d{2}\.\d{4})', available_text, re.IGNORECASE)
            available_date = available_match.group(1) if available_match else ""

            return {
                "id": apartment_id,
                "title": title,
                "address": address,
                "district": district,
                "rooms": rooms,
                "area": area,
                "rent": rent,
                "price_per_sqm": round(sqm_price, 2),
                "available_from": available_date,
                "url": detail_url,
                "found_at": datetime.now(self.berlin_timezone).isoformat()
            }
        
        except Exception as e:
            logger.error(f"Fehler beim Parsen einer Wohnung: {e}")
            return None

    def matches_filter(self, apartment):
        """Prüft, ob die Wohnung den Filterkriterien entspricht"""
        config = self.config
        
        # Grundlegende Filter
        if apartment["rooms"] < config["min_rooms"] or apartment["rooms"] > config["max_rooms"]:
            return False
            
        if apartment["area"] < config["min_area"] or apartment["area"] > config["max_area"]:
            return False
            
        if apartment["rent"] > config["max_rent"]:
            return False
            
        if apartment["price_per_sqm"] > config["max_price_per_sqm"]:
            return False
        
        # Bezirksfilter (falls konfiguriert)
        if config["districts"] and config["districts"][0]:  # Prüfen, ob Liste nicht leer ist
            # Normalisieren des Wohnungsbezirks für den Vergleich
            apartment_district = normalize_district(apartment["district"])
            
            # Normalisierte Bezirksnamen aus der Konfiguration
            normalized_config_districts = [normalize_district(d.strip()) for d in config["districts"]]
            
            # Prüfen, ob der Wohnungsbezirk in den konfigurierten Bezirken enthalten ist
            if apartment_district and apartment_district not in normalized_config_districts:
                return False
        
        return True

    def is_known_apartment(self, apartment):
        """Prüft, ob die Wohnung bereits bekannt ist"""
        return any(known["id"] == apartment["id"] for known in self.known_apartments)

    def send_notification(self, apartment):
        """Sendet eine Benachrichtigung über Telegram"""
        try:
            message = f"🏠 *Neue Wohnung gefunden!*\n"
            message += f"*{apartment['title']}*\n\n"
            message += f"🏙️ *Adresse:* {apartment['address']}\n"
            message += f"📍 *Bezirk:* {apartment['district']}\n"
            message += f"🚪 *Zimmer:* {apartment['rooms']}\n"
            message += f"📐 *Fläche:* {apartment['area']} m²\n"
            message += f"💰 *Warmmiete:* {apartment['rent']} €\n"
            message += f"📊 *Preis/m²:* {apartment['price_per_sqm']} €\n"
            message += f"📅 *Verfügbar ab:* {apartment['available_from']}\n"
            message += f"🔗 [Zum Angebot]({apartment['url']})"
            
            self.bot.send_message(
                chat_id=self.config["telegram_chat_id"],
                text=message,
                parse_mode=telegram.ParseMode.MARKDOWN,
                disable_web_page_preview=False
            )
            logger.info(f"Benachrichtigung für Wohnung {apartment['id']} gesendet")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Senden der Benachrichtigung: {e}")
            return False

    def scrape(self):
        """Hauptfunktion zum Scrapen der Website"""
        now = datetime.now(self.berlin_timezone)
        logger.info(f"Starte Scraping um {now.strftime('%H:%M:%S')}")
        
        try:
            url = "https://www.wbm.de/wohnungen-berlin/angebote/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            # Seite abrufen
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # HTML parsen
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Wohnungs-Divs finden
            apartment_divs = soup.find_all("div", class_="vacancy-tile")
            logger.info(f"{len(apartment_divs)} Wohnungsangebote gefunden")
            
            new_apartments_count = 0
            
            for div in apartment_divs:
                apartment = self.parse_apartment(div)
                
                if not apartment or not apartment["id"]:
                    continue
                
                # Prüfen, ob die Wohnung bereits bekannt ist
                if self.is_known_apartment(apartment):
                    continue
                
                # Prüfen, ob die Wohnung den Filterkriterien entspricht
                if self.matches_filter(apartment):
                    # Benachrichtigung senden
                    if self.send_notification(apartment):
                        new_apartments_count += 1
                
                # Wohnung zu den bekannten Wohnungen hinzufügen
                self.known_apartments.append(apartment)
            
            # Bekannte Wohnungen speichern
            self.save_known_apartments()
            
            if new_apartments_count > 0:
                logger.info(f"{new_apartments_count} neue passende Wohnungen gefunden und Benachrichtigungen gesendet")
            else:
                logger.info("Keine neuen passenden Wohnungen gefunden")
                
        except Exception as e:
            logger.error(f"Fehler beim Scraping: {e}")

def should_run_now():
    """Prüft, ob der Scraper jetzt laufen soll basierend auf Zeitplan"""
    config = load_config()
    now = datetime.now(pytz.timezone('Europe/Berlin'))
    
    # Tagesprüfung
    days_config = config["schedule_days"].lower()
    weekday = now.strftime('%a').lower()
    
    if days_config == "mon-fri" and weekday in ['sat', 'sun']:
        return False
    
    if days_config != "mon-sun" and days_config != "mon-fri":
        # Spezifische Tage prüfen
        allowed_days = days_config.split(',')
        if weekday not in allowed_days:
            return False
    
    # Uhrzeitprüfung
    hour = now.hour
    if hour < config["schedule_start_hour"] or hour >= config["schedule_end_hour"]:
        return False
    
    return True

def run_scraper():
    """Funktion zum Ausführen des Scrapers"""
    if should_run_now():
        config = load_config()
        scraper = WohnungScraper(config)
        scraper.scrape()
    else:
        logger.info("Scraper ist aktuell nicht für diese Zeit geplant")

def setup_schedule():
    """Zeitplan für den Scraper einrichten"""
    config = load_config()
    minutes = config["schedule_minutes"]
    
    logger.info(f"Plane Scraping alle {minutes} Minuten zwischen {config['schedule_start_hour']}:00 und {config['schedule_end_hour']}:00 Uhr")
    logger.info(f"An Tagen: {config['schedule_days']}")
    
    # Zeitplan einrichten (alle X Minuten)
    schedule.every(minutes).minutes.do(run_scraper)
    
    # Sofort einmal ausführen
    run_scraper()
    
    # Schedule-Loop
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    logger.info("WBM Wohnungsangebot-Scraper gestartet")
    setup_schedule()
