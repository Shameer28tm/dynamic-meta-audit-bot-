from playwright.sync_api import sync_playwright
import pandas as pd
import os

# Website pages to scan
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
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()

    for page_name, url in PAGES.items():
        print(f"Scraping: {page_name}")

        page = context.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_load_state("networkidle")

        data = extract_meta(page, page_name, url)

        df = pd.DataFrame(data)
        file_path = f"{OUTPUT_FOLDER}/{page_name}_meta.csv"
        df.to_csv(file_path, index=False, encoding="utf-8-sig")

        print(f"Saved: {file_path}")

        page.close()

    browser.close()

print("All meta tags extracted successfully.")
