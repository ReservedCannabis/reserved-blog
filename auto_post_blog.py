import os
import requests
import re
from bs4 import BeautifulSoup
from wordpress_rest_api import Client
from dotenv import load_dotenv
import random
import json
import time

load_dotenv()

WP_URL = os.getenv("WP_URL")
WP_USER = os.getenv("WP_USER")
WP_PASSWORD = os.getenv("WP_PASSWORD")
AFFILIATE_TAG = os.getenv("AFFILIATE_TAG", "smarthomepu07-20")

client = Client(WP_URL, WP_USER, WP_PASSWORD)

POST_DIR = "posts"
PROCESSED_LOG = "posted_articles.json"
AMAZON_SHEET = "AmazonAffiliateProducts"

# Load posted log
if os.path.exists(PROCESSED_LOG):
    with open(PROCESSED_LOG, "r") as f:
        posted = json.load(f)
else:
    posted = []

# Load product links
import gspread
sheet = gspread.service_account()
ws = sheet.open("InstagramAutoPosts").worksheet(AMAZON_SHEET)
products = ws.get_all_records()

def get_random_affiliate():
    product = random.choice(products)
    asin = product.get("asin", "")
    name = product.get("product_name", "")
    if asin:
        url = f"https://www.amazon.ca/dp/{asin}/?tag={AFFILIATE_TAG}"
        return f'<p><strong>Check this out:</strong> <a href="{url}" target="_blank">{name}</a></p>'
    return ""

def post_article(filepath):
    with open(filepath, "r") as f:
        soup = BeautifulSoup(f, "html.parser")

    title_tag = soup.find("h1")
    if not title_tag:
        print(f"⚠️ Skipping {filepath}, no H1 found.")
        return

    title = title_tag.text.strip()
    content = str(soup.find("div", class_="content")) if soup.find("div", class_="content") else str(soup.body)

    # Remove duplicate H1s
    content = re.sub(r"<h1>.*?</h1>", "", content)

    # Resize images
    content = re.sub(r'<img([^>]+)style="[^"]*"', r'<img\1', content)
    content = re.sub(r'<img', '<img style="max-width:100%;height:auto;"', content)

    # Add Amazon link
    affiliate_html = get_random_affiliate()
    if affiliate_html:
        content = content.replace("</p>", f"</p>{affiliate_html}", 1)

    # Fix slug
    slug = os.path.basename(filepath).replace(".html", "")
    slug = slug.replace("_", "-").replace(" ", "-").lower()

    # Post
    response = client.create_post({
        "title": title,
        "content": content,
        "status": "publish",
        "slug": slug
    })

    print(f"✅ Posted: {title}")
    posted.append(filepath)
    time.sleep(2)

# Main loop
for file in sorted(os.listdir(POST_DIR)):
    path = os.path.join(POST_DIR, file)
    if file.endswith(".html") and path not in posted:
        try:
            post_article(path)
        except Exception as e:
            print(f"❌ Failed to post {file}: {e}")

# Save log
with open(PROCESSED_LOG, "w") as f:
    json.dump(posted, f, indent=2)
