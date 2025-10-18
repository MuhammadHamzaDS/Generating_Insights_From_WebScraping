# # """
# # Web Scraper — Ready-to-use Python script (copy into your editor)

# # Usage:
# # 1. Put this file in your project folder or open in a code editor.
# # 2. Install dependencies: pip install requests beautifulsoup4 pandas
# # 3. Edit the CONFIG section below: set BASE_URL, START_PATH, and CSS_SELECTOR
# # 4. Run: python web_scraper_practice_script.py

# # This script is a reusable scraper template that:
# # - fetches pages with headers and timeout
# # - checks status codes
# # - parses HTML with BeautifulSoup
# # - extracts text using a CSS selector you provide
# # - handles simple pagination (by /page/X pattern)
# # - saves results to CSV
# # - includes polite sleeps and error handling

# # *** IMPORTANT: Always check robots.txt and site Terms of Service before scraping. ***

# # Created for learning and safe practice. For a specific site, change CONFIG accordingly.
# # """

# # import requests
# # from bs4 import BeautifulSoup
# # import time
# # import csv
# # import pandas as pd
# # from urllib.parse import urljoin


# # BASE_URL = "https://quotes.toscrape.com"
# # START_PATH = "/page/1/"   

# # ITEM_SELECTOR = "div.quote" 
# # TEXT_SELECTOR = "span.text"
# # AUTHOR_SELECTOR = "small.author"
# # TAGS_SELECTOR = "a.tag"

# # # Output file name
# # OUTPUT_CSV = "scraped_results.csv"

# # # Request headers
# # HEADERS = {
# #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
# #                   'AppleWebKit/537.36 (KHTML, like Gecko) '
# #                   'Chrome/91.0.4472.124 Safari/537.36'
# # }

# # # Politeness settings
# # SLEEP_BETWEEN_REQUESTS = 1.0  # seconds
# # MAX_PAGES = 50  # safety cap to avoid accidental huge crawls
# # TIMEOUT = 10

# # # ----------------------------------------------------

# # def fetch_page(url):
# #     try:
# #         resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
# #         return resp
# #     except requests.RequestException as e:
# #         print(f"Request failed: {e}")
# #         return None


# # def parse_items(html):
# #     soup = BeautifulSoup(html, 'html.parser')
# #     blocks = soup.select(ITEM_SELECTOR)
# #     items = []
# #     for b in blocks:
# #         text_el = b.select_one(TEXT_SELECTOR)
# #         author_el = b.select_one(AUTHOR_SELECTOR)
# #         tag_els = b.select(TAGS_SELECTOR)

# #         text = text_el.get_text(strip=True) if text_el else ""
# #         author = author_el.get_text(strip=True) if author_el else ""
# #         tags = ",".join([t.get_text(strip=True) for t in tag_els]) if tag_els else ""

# #         items.append({"text": text, "author": author, "tags": tags})

# #     return items


# # def save_to_csv(rows, filename=OUTPUT_CSV):
# #     if not rows:
# #         print("No rows to save.")
# #         return
# #     df = pd.DataFrame(rows)
# #     df.to_csv(filename, index=False, encoding='utf-8')
# #     print(f"Saved {len(rows)} rows to {filename}")


# # def run_scraper():
# #     results = []
# #     page = 1

# #     while page <= MAX_PAGES:
# #         # construct page URL - this assumes /page/X/ pattern
# #         path = f"/page/{page}/"
# #         url = urljoin(BASE_URL, path)
# #         print("Fetching:", url)

# #         resp = fetch_page(url)
# #         if resp is None:
# #             print("No response, stopping.")
# #             break

# #         if resp.status_code == 200:
# #             items = parse_items(resp.text)
# #             if not items:
# #                 print("No items found on this page — stopping pagination.")
# #                 break
# #             results.extend(items)
# #             page += 1
# #             time.sleep(SLEEP_BETWEEN_REQUESTS)
# #             continue
# #         elif resp.status_code in (301, 302):
# #             print(f"Redirected (status {resp.status_code}). Investigate URL: {url}")
# #             break
# #         elif resp.status_code == 404:
# #             print("Page not found (404). Stopping.")
# #             break
# #         else:
# #             print(f"Failed to retrieve the page. Status code: {resp.status_code}")
# #             break

# #     save_to_csv(results)


# # if __name__ == '__main__':
# #     print("Starting scraper (edit CONFIG at top to adapt to other sites)...")
# #     run_scraper()
# import requests
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin
# import pandas as pd
# import time

# BASE = "https://quotes.toscrape.com"
# HEADERS = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
#                   'AppleWebKit/537.36 (KHTML, like Gecko) '
#                   'Chrome/91.0.4472.124 Safari/537.36'
# }

# rows = []
# for page in range(1, 11):  # site has ~10 pages
#     url = f"{BASE}/page/{page}/"
#     print("Fetching", url)
#     resp = requests.get(url, headers=HEADERS, timeout=10)
#     if resp.status_code != 200:
#         print("Stopped, status:", resp.status_code)
#         break

#     soup = BeautifulSoup(resp.text, 'html.parser')
#     blocks = soup.select("div.quote")
#     if not blocks:
#         break

#     for b in blocks:
#         text = b.select_one("span.text").get_text(strip=True) if b.select_one("span.text") else ""
#         author = b.select_one("small.author").get_text(strip=True) if b.select_one("small.author") else ""

#         # Example: author page link is the first <a> inside the block that links to author page
#         a = b.find('a')  # this picks the first <a> (on this site it's the author link)
#         link = urljoin(BASE, a['href']) if a and a.get('href') else ""

#         # If you want ALL links inside the block:
#         # all_links = [urljoin(BASE, tag['href']) for tag in b.find_all('a', href=True)]

#         rows.append({"text": text, "author": author, "author_link": link})

#     time.sleep(1)  # be polite

# df = pd.DataFrame(rows)
# df.to_csv("quotes_with_links.csv", index=False, encoding='utf-8')
# print("Saved", len(df), "rows to quotes_with_links.csv")

"""
Robots.txt Checker + httpbin Response Demo

How to use:
1. Save this file and open in your editor.
2. Install dependencies (if not installed):
   pip install requests
3. Run:
   python robots_and_httpbin_demo.py

What this script does:
- Fetches and prints the site's robots.txt (if available)
- Parses Disallow rules and shows whether a given user-agent can fetch specific paths
- Demonstrates handling of common HTTP status codes using httpbin.org

DISCLAIMER: Use this script for learning and testing only. Do NOT use it to bypass site protections.
"""

import requests
from urllib import robotparser
from urllib.parse import urljoin


def fetch_and_print_robots(base_url):
    robots_url = base_url.rstrip('/') + '/robots.txt'
    print('\n--- Fetching robots.txt:', robots_url)
    try:
        r = requests.get(robots_url, timeout=10)
        print('\nrobots.txt content:\n')
        print(r.text)
        return r.text
    except requests.RequestException as e:
        print('Could not fetch robots.txt:', e)
        return None


def parse_robots(base_url, user_agent='*'):
    rp = robotparser.RobotFileParser()
    rp.set_url(base_url.rstrip('/') + '/robots.txt')
    try:
        rp.read()
    except Exception as e:
        print('robotparser could not read robots.txt:', e)
        return None

    # simple checks
    print(f"\nCan user-agent '{user_agent}' fetch homepage? ->", rp.can_fetch(user_agent, urljoin(base_url, '/')))
    test_paths = ['/','/login','/search','/admin']
    print('\nCheck some common paths:')
    for p in test_paths:
        print(f"  {p}:", rp.can_fetch(user_agent, urljoin(base_url, p)))

    return rp


def httpbin_demo():
    print('\n--- httpbin status demo')
    tests = {
        'OK (200)': 'https://httpbin.org/status/200',
        'Forbidden (403)': 'https://httpbin.org/status/403',
        'Too Many Requests (429)': 'https://httpbin.org/status/429',
        'Not Found (404)': 'https://httpbin.org/status/404'
    }
    for name, url in tests.items():
        try:
            r = requests.get(url, timeout=10)
            print(f"{name}: {r.status_code}")
            if r.status_code == 200:
                print('  -> OK: safe to proceed (for demo)')
            elif r.status_code == 403:
                print('  -> Forbidden: access denied; do NOT try to bypass this')
            elif r.status_code == 429:
                print('  -> Rate limited: slow down requests')
            else:
                print('  -> Response code shows this resource is not available or restricted')
        except requests.RequestException as e:
            print(f"Request to {url} failed:", e)


if __name__ == '__main__':
    print('Robots.txt & httpbin demo - edit the TARGET_SITE variable below to test a site')

    # ----- CONFIGURE THIS -----
    TARGET_SITE = 'https://www.amazon.com/robots.txt'  # <- change this to the site you want to check
    USER_AGENT = 'Mozilla/5.0 (compatible; MyScraper/1.0)'
    # --------------------------

    fetch_and_print_robots(TARGET_SITE)
    parse_robots(TARGET_SITE, user_agent=USER_AGENT)
    httpbin_demo()

