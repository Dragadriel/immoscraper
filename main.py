# main.py (mit Playwright für JavaScript-Rendering)
import os
import asyncio
import datetime
import subprocess

# Fallback: Stelle sicher, dass die Playwright-Browser installiert sind
subprocess.run(["playwright", "install", "--with-deps"], check=True)
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import requests

load_dotenv()

IS24_URL = os.getenv("IS24_URL")
NO_GO_KEYWORDS = os.getenv("NO_GO_KEYWORDS", "möbliert,befristet,staffelmiete,zwischenmiete,untermiete,wg").lower().split(',')
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
LAST_IDS_FILE = "last_ids.txt"
TEST_MODE = os.getenv("TEST_BOT", "false").lower() == "true"


def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def fetch_results():
    with sync_playwright() as p:
        log(f"Starte Headless-Browser für Seite: {IS24_URL}")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(IS24_URL, timeout=60000)
        
        # Warte auf ein spezifisches Element, das sicherstellt, dass die Seite vollständig geladen ist
        page.wait_for_selector('[data-obid]', timeout=30000)  # Warte auf ein Element mit der data-obid, das normalerweise alle Inserate enthält

        html = page.content()
        soup = BeautifulSoup(html, "html.parser")
        listings = soup.select('[data-obid]')
        log(f"{len(listings)} Inserate auf der Seite gefunden")

        results = []
        filtered_out = 0
        for listing in listings:
            obid = listing.get("data-obid")
            title = listing.get_text(" ", strip=True).lower()
            link = f"https://www.immobilienscout24.de/expose/{obid}"
            if not any(kw in title for kw in NO_GO_KEYWORDS):
                results.append((obid, link, title))
            else:
                filtered_out += 1

        log(f"{len(results)} passende Ergebnisse nach No-Go-Filter")
        log(f"{filtered_out} Inserate aufgrund von No-Go-Keywords herausgefiltert")
        browser.close()
        return results


def load_last_ids():
    try:
        with open(LAST_IDS_FILE, "r") as f:
            return set(f.read().splitlines())
    except FileNotFoundError:
        return set()


def save_ids(ids):
    with open(LAST_IDS_FILE, "w") as f:
        f.write("\n".join(ids))


def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "disable_web_page_preview": True}
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        log("Telegram-Nachricht erfolgreich gesendet")
    else:
        log(f"Fehler beim Senden der Telegram-Nachricht: {response.text}")


def main():
    if TEST_MODE:
        log("Testmodus aktiv – Sende Testnachricht an Telegram")
        send_telegram_message("✅ Der ImmoBot ist erfolgreich verbunden und betriebsbereit.")
        return

    last_ids = load_last_ids()
    log(f"{len(last_ids)} bekannte Inserate geladen")

    current_results = fetch_results()
    new_ids = []

    for obid, link, title in current_results:
        if obid not in last_ids:
            log(f"Neues Inserat entdeckt: {obid}")
            message = f"🏠 Neues Inserat gefunden:\n{link}\n\nTitel: {title}"
            send_telegram_message(message)
            new_ids.append(obid)

    if new_ids:
        save_ids(last_ids.union(new_ids))
        log(f"{len(new_ids)} neue Inserate gespeichert")
    else:
        log("Keine neuen Inserate gefunden")


if __name__ == "__main__":
    main()
