from playwright.sync_api import sync_playwright
from urllib.parse import urljoin, urlparse
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import re
import webbrowser

SPREADSHEET_ID = "1opy0hnidSahD7a_-ecxtOFwhYkaY7P6sElPfxkfzNdk"
CREDENTIALS_FILE = "google_credentials.json"

# ---------- GOOGLE AUTH ----------
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
client = gspread.authorize(creds)
spreadsheet = client.open_by_key(SPREADSHEET_ID)

# ---------- HELPERS ----------

def clean_sheet_name(url):
    name = url.replace("https://", "").replace("http://", "")
    name = re.sub(r"[^a-zA-Z0-9]", "_", name)
    return name[:90]

def get_internal_links(page, base_url):
    anchors = page.query_selector_all("a[href]")
    links = set()
    domain = urlparse(base_url).netloc

    for a in anchors:
        href = a.get_attribute("href")
        if href:
            full = urljoin(base_url, href)
            parsed = urlparse(full)
            if parsed.netloc == domain and full.startswith("http"):
                links.add(full.split("#")[0])
    return list(links)

def extract_meta(page, url):
    tags = page.query_selector_all("meta")
    print("   Meta tags found:", len(tags))
    rows = []

    for tag in tags:
        rows.append([
            url,
            tag.get_attribute("name"),
            tag.get_attribute("property"),
            tag.get_attribute("http-equiv"),
            tag.get_attribute("content")
        ])

    return rows

# ---------- USER INPUT ----------

base_url = input("\nEnter website URL: ").strip()

# ---------- CRAWLER ----------

visited = set()
to_visit = [base_url]
MAX_PAGES = 15

all_results = {}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # visible
    context = browser.new_context()

    while to_visit and len(visited) < MAX_PAGES:
        url = to_visit.pop(0)
        if url in visited:
            continue

        print("\nOpening:", url)
        visited.add(url)

        page = context.new_page()
        try:
            page.goto(url, timeout=60000)
            page.wait_for_load_state("networkidle")

            meta = extract_meta(page, url)
            all_results[url] = meta

            new_links = get_internal_links(page, base_url)
            print("   New internal links found:", len(new_links))

            for link in new_links:
                if link not in visited and link not in to_visit:
                    to_visit.append(link)

        except Exception as e:
            print("   ERROR loading:", url, str(e))

        page.close()

    browser.close()

# ---------- UPLOAD TO GOOGLE SHEETS ----------

print("\nUploading to Google Sheets...")

for url, rows in all_results.items():
    if not rows:
        continue

    headers = ["page_url", "name", "property", "http_equiv", "content"]
    df = pd.DataFrame(rows, columns=headers)

    sheet_name = clean_sheet_name(url)

    try:
        ws = spreadsheet.worksheet(sheet_name)
        ws.clear()
    except:
        ws = spreadsheet.add_worksheet(title=sheet_name, rows="300", cols="10")

    ws.update([headers] + df.values.tolist())
    print("Uploaded sheet:", sheet_name)

print("\nDONE. Pages crawled:", len(all_results))

# ---------- OPEN SHEET ----------

sheet_url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}"
webbrowser.open(sheet_url)
