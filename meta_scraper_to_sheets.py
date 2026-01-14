from playwright.sync_api import sync_playwright
import pandas as pd
import os
import time

PAGES = {
    "home": "https://zclouddigitech.com/",
    "about": "https://zclouddigitech.com/about",
    "services": "https://zclouddigitech.com/services",
    "contact": "https://zclouddigitech.com/contact"
}

OUTPUT_FOLDER = "meta_output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def extract_meta(page, page_name, page_url):
    meta_tags = page.query_selector_all("meta")
    records = []

    for tag in meta_tags:
        records.append({
            "page": page_name,
            "page_url": page_url,
            "name": tag.get_attribute("name"),
            "property": tag.get_attribute("property"),
            "http_equiv": tag.get_attribute("http-equiv"),
            "content": tag.get_attribute("content")
        })

    return records


with sync_playwright() as p:
    # ---------- PART 1: SCRAPE META TAGS ----------
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()

    created_files = []

    for page_name, url in PAGES.items():
        page = context.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_load_state("networkidle")

        data = extract_meta(page, page_name, url)
        df = pd.DataFrame(data)

        file_path = f"{OUTPUT_FOLDER}/{page_name}_meta.csv"
        df.to_csv(file_path, index=False, encoding="utf-8-sig")
        created_files.append(os.path.abspath(file_path))

        page.close()

    browser.close()

    print("Meta extraction completed.")

    # ---------- PART 2: OPEN GOOGLE SHEETS + UPLOAD ----------
    browser = p.chromium.launch(headless=False)  # visible for login
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://sheets.google.com")
    page.wait_for_timeout(5000)

    # If not logged in, login manually once
    if "accounts.google.com" in page.url:
        print("Please login manually. After login, press ENTER in terminal.")
        input()
        context.storage_state(path="google_login.json")
        print("Login saved. Re-run script.")
        browser.close()
        exit()

    for file in created_files:
        page.goto("https://sheets.google.com")
        page.wait_for_timeout(3000)

        page.click("text=Blank")
        page.wait_for_timeout(3000)

        page.click("text=File")
        page.click("text=Import")
        page.wait_for_timeout(2000)

        page.click("text=Upload")
        file_input = page.locator("input[type=file]")
        file_input.set_input_files(file)

        page.wait_for_timeout(8000)
        page.click("text=Import data")
        page.wait_for_timeout(5000)

        print("Uploaded:", file)

    print("All files uploaded to Google Sheets.")
