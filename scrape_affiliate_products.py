
import requests
import random
import time
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# === CONFIG ===
SHEET_ID = "10RTloEY5nvjOBm7CaPhYMplxbY31Gf8CMVFkXVAW2to"
TAB_NAME = "AffiliateProducts"
AFFILIATE_TAG = "smarthomepu07-20"
KEYWORDS = [
    "cannabis grinder", "rolling tray", "stash box", "smell proof bag",
    "weed scale", "cannabis accessories", "weed storage", "cannabis container",
    "pre-roll kit", "herb trimmer", "humidity packs"
]

# === SETUP SHEETS ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("google-credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(TAB_NAME)
existing_asins = [row[1] for row in sheet.get_all_values()[1:]]

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-CA,en;q=0.9"
}

def extract_asin(url):
    parts = url.split("/dp/")
    if len(parts) > 1:
        asin = parts[1].split("/")[0].split("?")[0]
        return asin
    return None

def scrape_amazon(keyword):
    base_url = "https://www.amazon.ca/s"
    params = {"k": keyword}
    print(f"🔍 Searching: {keyword}")
    res = requests.get(base_url, headers=headers, params=params)
    soup = BeautifulSoup(res.text, "html.parser")
    products = []
    for div in soup.select("div[data-asin]"):
        asin = div.get("data-asin")
        if not asin or asin in existing_asins:
            continue
        title_tag = div.select_one("h2 a span")
        if not title_tag:
            continue
        title = title_tag.text.strip()
        link_tag = div.select_one("h2 a")
        if not link_tag:
            continue
        url = "https://www.amazon.ca" + link_tag.get("href").split("?")[0]
        full_url = f"https://www.amazon.ca/dp/{asin}/?tag={AFFILIATE_TAG}"
        products.append([title, asin, keyword, full_url])
        if len(products) >= 15:
            break
    return products

# === RUN SCRAPER ===
all_products = []
random.shuffle(KEYWORDS)

for kw in KEYWORDS:
    found = scrape_amazon(kw)
    all_products.extend(found)
    time.sleep(3)

# === WRITE TO SHEET ===
if all_products:
    rows = [[p[0], p[1], p[2], p[3]] for p in all_products]
    sheet.append_rows(rows, value_input_option="RAW")
    print(f"✅ Added {len(rows)} new products to Google Sheets.")
else:
    print("❌ No products found.")
