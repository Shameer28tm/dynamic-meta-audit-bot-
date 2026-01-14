from playwright.sync_api import sync_playwright
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ================= CONFIG =================

SPREADSHEET_ID = "1opy0hnidSahD7a_-ecxtOFwhYkaY7P6sElPfxkfzNdk"

PAGES = {
    "Home": "https://zclouddigitech.com/",
    "About": "https://zclouddigitech.com/about",
    "Services": "https://zclouddigitech.com/services",
    "Contact": "https://zclouddigitech.com/contact"
}

CREDENTIALS_FILE = "google_credentials.json"

# ================= GOOGLE AUTH =================

scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
client = gspread.authorize(creds)
spreadsheet = client.open_by_key(SPREADSHEET_ID)

# ================= PLAYWRIGHT SCRAPER =================

def extract_meta(page, page_name, page_url):
    meta_tags = page.query_selector_all("meta")
    data = []

    for tag in meta_tags:
        data.append([
            page_name,
            page_url,
            tag.get_attribute("name"),
            tag.get_attribute("property"),
            tag.get_attribute("http-equiv"),
            tag.get_attribute("content")
        ])

    return data

# ================= MAIN =================

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()

    for sheet_name, url in PAGES.items():
        print("Scraping:", sheet_name)

        page = context.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_load_state("networkidle")

        rows = extract_meta(page, sheet_name, url)

        headers = ["page", "page_url", "name", "property", "http_equiv", "content"]
        df = pd.DataFrame(rows, columns=headers)

        try:
            worksheet = spreadsheet.worksheet(sheet_name)
            worksheet.clear()
        except:
            worksheet = spreadsheet.add_worksheet(title=sheet_name, rows="1000", cols="10")

        worksheet.update([headers] + df.values.tolist())

        print("Uploaded:", sheet_name)

        page.close()

    browser.close()

print("ALL META TAGS SENT TO GOOGLE SHEETS SUCCESSFULLY")

import webbrowser

sheet_url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}"
webbrowser.open(sheet_url)
