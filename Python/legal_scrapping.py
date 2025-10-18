"""
Legal Scraping Workflow & Practical Examples (editor-friendly)

Open this file in your code editor. It contains:
1) Short legal checklist before scraping
2) Robots.txt checker (runnable)
3) httpbin status demo (runnable) - shows 200,403,429,404
4) Authenticated scraping template using requests.Session (ONLY use if you own the account or have permission)
5) Safe scraping template for a practice site (quotes.toscrape.com)
6) Exponential backoff helper + retry wrapper (reusable)
7) How to run and notes

IMPORTANT: Do NOT use any code here to bypass site protections, break captchas, or access private data without explicit permission.

Save file and run with: python Legal_Scraping_Workflow_and_Examples.py

"""

# ---------------- CONFIG - edit before running ----------------
TARGET_SITE = ""  # change to site you want to check (for robots.txt check only)
PRACTICE_SITE = "https://www.amazon.com/robots.txt  "  # safe practice site
USER_AGENT = "MyScraper/1.0 (email@example.com)"
# ----------------------------------------------------------------

import time
import requests
from urllib import robotparser
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import pandas as pd

# ------------------ Helper: Exponential backoff ------------------

def exponential_backoff_sleep(attempt, base=1, factor=2, jitter=0.0):
    """Sleep using exponential backoff. attempt starts at 1."""
    wait = base * (factor ** (attempt - 1))
    if jitter:
        wait = wait * (1 + jitter * (2 * (0.5 - 0.5)))
    time.sleep(wait)


# ------------------ 1) Legal checklist (printable) ------------------

def print_legal_checklist():
    print("\n=== LEGAL CHECKLIST BEFORE SCRAPING ===")
    print("1. Check robots.txt (https://site/robots.txt)")
    print("2. Search for an official API and prefer it")
    print("3. Read Terms of Service for allowed use")
    print("4. If no API, contact site owner and get written permission")
    print("5. If permitted, follow rate limits, headers, and logging rules")


# ------------------ 2) Robots.txt checker (runnable) ------------------

def fetch_and_print_robots(base_url):
    robots_url = base_url.rstrip('/') + '/robots.txt'
    print(f"\nFetching robots.txt from: {robots_url}")
    try:
        r = requests.get(robots_url, timeout=10)
        print('\n----- robots.txt content -----')
        print(r.text)
        print('----- end robots.txt -----\n')
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

    print(f"Can user-agent '{user_agent}' fetch homepage? ->", rp.can_fetch(user_agent, urljoin(base_url, '/')))
    test_paths = ['/', '/login', '/search', '/admin']
    print('\nCheck some common paths:')
    for p in test_paths:
        print(f"  {p} ->", rp.can_fetch(user_agent, urljoin(base_url, p)))

    return rp


# ------------------ 3) httpbin status demo (runnable) ------------------

def httpbin_status_demo():
    print('\n--- httpbin status demo ---')
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
                print('  -> OK: safe to proceed (demo)')
            elif r.status_code == 403:
                print('  -> Forbidden: access denied; do NOT try to bypass this')
            elif r.status_code == 429:
                print('  -> Rate limited: slow down requests')
            else:
                print('  -> Response shows this resource is not available or restricted')
        except requests.RequestException as e:
            print(f"Request to {url} failed:", e)


# ------------------ 4) Authenticated scraping template ------------------
# Use ONLY if you own the account or have explicit written permission

def authenticated_scrape_template(login_url, protected_url, username, password):
    print('\n--- Authenticated scrape template (demo only) ---')
    session = requests.Session()
    session.headers.update({'User-Agent': USER_AGENT})

    payload = {'username': username, 'password': password}
    try:
        r = session.post(login_url, data=payload, timeout=15)
        print('Login status:', r.status_code)
        if r.status_code != 200:
            print('Login failed or requires more steps (e.g., CSRF).')
            return None

        r2 = session.get(protected_url, timeout=15)
        print('Protected page status:', r2.status_code)
        if r2.status_code == 200:
            soup = BeautifulSoup(r2.text, 'html.parser')
            return soup
        else:
            print('Could not retrieve protected page. Status:', r2.status_code)
            return None
    except requests.RequestException as e:
        print('Request error during authenticated flow:', e)
        return None


# ------------------ 5) Safe practice scraper (quotes.toscrape.com) ------------------

def safe_quotes_scraper(max_pages=10):
    print('\n--- Running safe scraper on practice site ---')
    base = PRACTICE_SITE
    headers = {'User-Agent': USER_AGENT}
    results = []

    for page in range(1, max_pages + 1):
        url = f"{base}/page/{page}/"
        print('Fetching', url)
        try:
            r = requests.get(url, headers=headers, timeout=10)
        except requests.RequestException as e:
            print('Request failed:', e)
            break

        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            blocks = soup.select('div.quote')
            if not blocks:
                print('No items found on this page — stopping.')
                break
            for b in blocks:
                text = b.select_one('span.text').get_text(strip=True) if b.select_one('span.text') else ''
                author = b.select_one('small.author').get_text(strip=True) if b.select_one('small.author') else ''
                a = b.find('a', href=True)
                author_link = urljoin(base, a['href']) if a and a.get('href') else ''
                tags = ','.join([t.get_text(strip=True) for t in b.select('a.tag')])
                results.append({'text': text, 'author': author, 'author_link': author_link, 'tags': tags})
            time.sleep(1)
            continue
        elif r.status_code == 404:
            print('404 Not Found — stopping.')
            break
        elif r.status_code == 429:
            print('429 Rate limited — backing off for 30s')
            time.sleep(30)
            continue
        else:
            print('Unhandled status', r.status_code)
            break

    if results:
        df = pd.DataFrame(results)
        df.to_csv('quotes_practice.csv', index=False, encoding='utf-8')
        print('Saved', len(results), 'rows to quotes_practice.csv')
    else:
        print('No data scraped.')


# ------------------ 6) Small demo runner ------------------

if __name__ == '__main__':
    print_legal_checklist()

    # 1) Robots.txt demo (prints file and a few checks)
    fetch_and_print_robots(TARGET_SITE)
    parse_robots(TARGET_SITE, user_agent=USER_AGENT)

    # 2) httpbin demo
    httpbin_status_demo()

    # 3) Safe practice scraping (uncomment to run)
    # safe_quotes_scraper(max_pages=5)

    # 4) Authenticated template (DO NOT run unless you own account and set real credentials)
    # authenticated_scrape_template('https://target/login', 'https://target/protected', 'username', 'password')

    print('\nDemo complete. Edit TARGET_SITE and other values at top before re-running.')
