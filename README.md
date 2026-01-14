# Meta Scraper (Playwright)

A small collection of Python scripts to extract meta and page metadata from websites and save the results to CSV or Google Sheets.

**Contents**
- `meta_scraper.py` — core scraper utilities
- `dynamic_meta_to_sheets.py` — run dynamic scraping and save results
- `dynamic_pagewise_meta_to_sheets.py` — scrape pages per site and export
- `meta_scraper_to_sheets.py` — export collected data to local CSVs
- `meta_scraper_to_google_sheets.py` — push results to Google Sheets
- `meta_output/` — output CSV files (e.g. `home_meta.csv`, `about_meta.csv`)

**Requirements**
- Python 3.10+
- Playwright
- pandas
- If using Google Sheets export: `gspread`, `google-auth` (or similar)

Install common dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt  # if present
pip install playwright pandas
playwright install
```

If you plan to push to Google Sheets, install and configure your service account credentials and the required packages.

**Usage (examples)**
- Run the simple scraper:

```bash
python meta_scraper.py
```

- Run the dynamic, page-wise scraper:

```bash
python dynamic_pagewise_meta_to_sheets.py
```

- Export to local CSVs (checks `meta_output/`):

```bash
python meta_scraper_to_sheets.py
```

- Push results to Google Sheets (provide credentials file or environment variables as required by your setup):

```bash
python meta_scraper_to_google_sheets.py --credentials ./path/to/creds.json
```

Note: Adjust command-line arguments and inputs according to each script's docstring or help text.

**Output**
- Scraped metadata CSVs are written to the `meta_output/` folder by default.

**Configuration**
- Provide target URLs either by editing the scripts, passing input files, or following each script's expected input (see top-of-file comments).
- For Google Sheets, create a service account, download the JSON credentials, and point the script to that file or set the appropriate environment variables.

**Contributing**
- Fixes and improvements welcome via issues and pull requests.

**License**
- No license specified.
