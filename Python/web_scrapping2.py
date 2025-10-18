"""
Safe Quotes Scraper (practice)
- Site: https://quotes.toscrape.com  (practice-friendly)
- Extracts: quote text, author, author page link, tags
- Saves to: quotes_safe.csv

How to run:
1) pip install requests beautifulsoup4 pandas
2) python quotes_scraper_safe.py
"""

import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd

BASE = "https://www.amazon.com/robots.txt"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/91.0.4472.124 Safari/537.36"
}

MAX_PAGES = 20           # safety cap
SLEEP_BETWEEN_REQUESTS = 1.0
TIMEOUT = 10             # seconds for each request
MAX_RETRIES = 3          # retry on timeout or 5xx
BACKOFF_FACTOR = 2       # exponential backoff multiplier

def get_with_retries(url):
    """GET with simple retries and exponential backoff for safe handling."""
    wait = 1
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            return resp
        except requests.exceptions.ReadTimeout:
            print(f"Timeout on attempt {attempt} for {url}")
        except requests.exceptions.RequestException as e:
            print(f"Request error on attempt {attempt}: {e}")
        # backoff before next attempt
        time.sleep(wait)
        wait *= BACKOFF_FACTOR
    return None

def parse_quote_block(block):
    """Extract quote text, author, link, tags from a quote block."""
    text_el = block.select_one("span.text")
    author_el = block.select_one("small.author")
    # find author link specifically (the <a href="/author/..."> element)
    a = block.find('a', href=True)
    tag_els = block.select("a.tag")

    text = text_el.get_text(strip=True) if text_el else ""
    author = author_el.get_text(strip=True) if author_el else ""
    author_link = urljoin(BASE, a['href']) if a and a.get('href') else ""
    tags = ",".join([t.get_text(strip=True) for t in tag_els]) if tag_els else ""

    return {"text": text, "author": author, "author_link": author_link, "tags": tags}

def run_scraper():
    results = []
    for page in range(1, MAX_PAGES + 1):
        url = f"{BASE}/page/{page}/"
        print(f"Fetching: {url}")

        resp = get_with_retries(url)
        if resp is None:
            print("No response after retries — stopping.")
            break

        # handle common status codes
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            blocks = soup.select("div.quote")
            if not blocks:
                print("No items found on this page — stopping pagination.")
                break

            for b in blocks:
                item = parse_quote_block(b)
                results.append(item)

            # be polite
            time.sleep(SLEEP_BETWEEN_REQUESTS)
            continue

        elif resp.status_code == 403:
            print("403 Forbidden — site blocked this request. Stop and check permissions.")
            break
        elif resp.status_code == 429:
            # rate limited: back off then try next page (or stop)
            print("429 Too Many Requests — backing off for 30 seconds then continuing.")
            time.sleep(30)
            continue
        elif resp.status_code == 404:
            print("404 Not Found — no more pages or wrong URL. Stopping.")
            break
        else:
            print(f"Unhandled status {resp.status_code} — stopping.")
            break

    # Save results
    if results:
        df = pd.DataFrame(results)
        df.to_csv("quotes_safe.csv", index=False, encoding="utf-8")
        print(f"Saved {len(results)} rows to quotes_safe.csv")
    else:
        print("No data scraped.")

if __name__ == "__main__":
    run_scraper()
