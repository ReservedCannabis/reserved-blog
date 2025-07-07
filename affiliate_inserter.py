import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import random

AFFILIATE_TAG = "smarthomepu07-20"  # Replace with your real tag

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("google-credentials.json", scope)
client = gspread.authorize(creds)

sheet = client.open_by_key("10RTloEY5nvjOBm7CaPhYMplxbY31Gf8CMVFkXVAW2to").worksheet("AffiliateProducts")
data = sheet.get_all_records()
products = [p for p in data if p["asin"] and p["product_name"]]

html_files = sorted(f for f in os.listdir("posts") if f.endswith(".html"))
random.shuffle(products)

for idx, file in enumerate(html_files):
    if idx >= len(products): break
    filepath = os.path.join("posts", file)
    asin = products[idx]["asin"].strip()
    name = products[idx]["product_name"].strip()
    aff_link = f"https://www.amazon.ca/dp/{asin}/?tag={AFFILIATE_TAG}"
    caption = f'<p style="margin-top:20px;"><strong>Featured Product:</strong> <a href="{aff_link}" target="_blank" style="color:#ffd54f;">{name}</a> – A top-rated cannabis accessory on Amazon Canada.</p>'

    with open(filepath, "r") as f:
        content = f.read()

    # Ensure readable white text and append affiliate link
    if "<style>" not in content:
        content = content.replace("<body>", """<body>
<style>body{color:#fff;font-size:1.2em;line-height:1.6;}</style>""")
    content += caption

    with open(filepath, "w") as f:
        f.write(content)

    print(f"✅ Injected affiliate product: {name} → {file}")

print(f"\n✅ Done! {min(len(html_files), len(products))} inserted, {max(0, len(html_files) - len(products))} skipped.")