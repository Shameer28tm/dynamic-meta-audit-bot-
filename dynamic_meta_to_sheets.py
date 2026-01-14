from playwright.sync_api import sync_playwright
from urllib.parse import urljoin, urlparse
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import webbrowser

# ================= GOOGLE CONFIG =================

SPREADSHEET_ID = "1opy0hnidSahD7a_-ecxtOFwhYkaY7P6sElPfxkfzNdk"
CREDENTIALS_FILE = "google_credentials.json"
MASTER_SHEET_NAME = "META_AUDIT"

# ================= GOOGLE AUTH =================

scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
client = gspread.authorize(creds)
spreadsheet = client.open_by_key(SPREADSHEET_ID)

try:
    worksheet = spreadsheet.worksheet(MASTER_SHEET_NAME)
    worksheet.clear()
except:
    worksheet = spreadsheet.add_worksheet(title=MASTER_SHEET_NAME, rows="2000", cols="10")

# ================= CRAWLER FUNCTIONS =================

def get_internal_links(page, base_url):
    anchors = page.query_selector_all("a[href]")
    links = set()
    domain = urlparse(base_url).netloc

    for a in anchors:
        href = a.get_attribute("href")
        if href:
            full_url = urljoin(base_url, href)
            parsed = urlparse(full_url)

            if parsed.netloc == domain and full_url.startswith("http"):
                links.add(full_url.split("#")[0])

    return list(links)

def extract_meta(page, url):
    tags = page.query_selector_all("meta")
    data = []

    for tag in tags:
        data.append([
            url,
            tag.get_attribute("name"),
            tag.get_attribute("property"),
            tag.get_attribute("http-equiv"),
            tag.get_attribute("content")
        ])

    return data

# ================= USER INPUT =================

base_url = input("\nEnter website URL (https://...): ").strip()

# ================= CRAWL ENGINE =================

visited = set()
to_visit = [base_url]
all_rows = []

MAX_PAGES = 30  # safety limit

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()

    while to_visit and len(visited) < MAX_PAGES:
        url = to_visit.pop(0)
        if url in visited:
            continue

        print("Crawling:", url)
        visited.add(url)

        page = context.new_page()
        try:
            page.goto(url, timeout=60000)
            page.wait_for_load_state("networkidle")

            all_rows.extend(extract_meta(page, url))

            new_links = get_internal_links(page, base_url)
            for link in new_links:
                if link not in visited and link not in to_visit:
                    to_visit.append(link)

        except:
            print("Skipped:", url)

        page.close()

    browser.close()

# ================= SEND TO GOOGLE SHEETS =================

headers = ["page_url", "name", "property", "http_equiv", "content"]
df = pd.DataFrame(all_rows, columns=headers)

worksheet.update([headers] + df.values.tolist())

print("\nMETA AUDIT COMPLETED SUCCESSFULLY")
print("Pages crawled:", len(visited))
print("Total meta tags:", len(all_rows))

# ================= OPEN SHEET =================

sheet_url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}"
webbrowser.open(sheet_url)
