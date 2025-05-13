# main.py
import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

IS24_URL = os.getenv("IS24_URL")
NO_GO_KEYWORDS = os.getenv("NO_GO_KEYWORDS", "möbliert,befristet,staffelmiete,zwischenmiete,untermiete,wg").lower().split(',')
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
LAST_IDS_FILE = "last_ids.txt"


def fetch_results():
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(IS24_URL, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    listings = soup.select('[data-obid]')
    results = []
    for listing in listings:
        obid = listing.get("data-obid")
        title = listing.get_text(" ", strip=True).lower()
        link = f"https://www.immobilienscout24.de/expose/{obid}"
        if not any(kw in title for kw in NO_GO_KEYWORDS):
            results.append((obid, link, title))
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
    requests.post(url, data=payload)


def main():
    last_ids = load_last_ids()
    current_results = fetch_results()
    new_ids = []

    for obid, link, title in current_results:
        if obid not in last_ids:
            message = f"🏠 Neues Inserat gefunden:\n{link}\n\nTitel: {title}"
            send_telegram_message(message)
            new_ids.append(obid)

    if new_ids:
        save_ids(last_ids.union(new_ids))


if __name__ == "__main__":
    main()
