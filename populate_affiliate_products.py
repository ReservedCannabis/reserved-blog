#!/usr/bin/env python3
import gspread
from google.oauth2.service_account import Credentials
import datetime

# === CONFIG ===
SHEET_ID     = "10RTloEY5nvjOBm7CaPhYMplxbY31Gf8CMVFkXVAW2to"
TAB_NAME     = "AffiliateProducts"     # exactly your sheet tab
GOOGLE_CRED  = "google-credentials.json"
AFF_TAG      = "smarthomepu07-20"

# 15 known-good Canadian cannabis accessory ASINs + names
PRODUCTS = [
    ("Electric Herb Grinder",        "B08L8V7R5K"),
    ("2-Piece Aluminum Grinder",     "B07P1F6Y7D"),
    ("Large Rolling Tray",           "B06XFG9N46"),
    ("Precision Digital Weed Scale", "B07ZTCYRGR"),
    ("Airtight Stash Jar",           "B07JP61GNC"),
    ("Smell-Proof Storage Bag",      "B089KFG4R9"),
    ("UV-Protected Glass Jar",       "B00F30RYSQ"),
    ("Smell-Proof Case",             "B08BLHLP6M"),
    ("Organic Hemp Rolling Papers",  "B071FSTJFT"),
    ("Mini LED Weed Magnifier",      "B08L5SRN8V"),
    ("Boveda 62% Humidity Packs",    "B07FDMCGC5"),
    ("Magnetic Stash Box",           "B07MMPZ32Y"),
    ("Organizer Weed Container",     "B08S4V2Y5G"),
    ("Portable Herb Trimmer",        "B07JKV5ZQW"),
    ("Pre-Roll Cone Filler",         "B07XSJ1R2W"),
]

def main():
    # auth
    scopes = ["https://www.googleapis.com/auth/spreadsheets",
              "https://www.googleapis.com/auth/drive"]
    creds  = Credentials.from_service_account_file(GOOGLE_CRED, scopes=scopes)
    client = gspread.authorize(creds)
    ws     = client.open_by_key(SHEET_ID).worksheet(TAB_NAME)

    # read existing ASINs to avoid dupes
    existing = { row["asin"] for row in ws.get_all_records() if row.get("asin") }

    added = 0
    for name, asin in PRODUCTS:
        if asin in existing:
            print(f"↪ skip (already in sheet): {asin}")
            continue

        url = f"https://www.amazon.ca/dp/{asin}/?tag={AFF_TAG}"
        timestamp = datetime.datetime.utcnow().isoformat()
        ws.append_row([name, asin, url, timestamp])
        print(f"✅ Added: {name} → {url}")
        added += 1

    print(f"\n🎉 Done. {added} new products appended.")

if __name__ == "__main__":
    main()
