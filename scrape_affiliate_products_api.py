import boto3
import hashlib
import hmac
import base64
import json
import requests
import time
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from urllib.parse import quote, urlencode

# === CONFIG ===
AWS_ACCESS_KEY = "AKPA76WINC1750936089"
AWS_SECRET_KEY = "R27sm7NoWPzE+Zvftji0eBNMyNg1umtVNQOP9wux"
ASSOCIATE_TAG = "smarthomepu07-20"
MARKETPLACE = "webservices.amazon.ca"
REGION = "ca-central-1"
SHEET_ID = "10RTloEY5nvjOBm7CaPhYMplxbY31Gf8CMVFkXVAW2to"
SHEET_TAB = "AffiliateProducts"

KEYWORDS = [
    "cannabis grinder", "rolling tray", "stash box", "smell proof bag", "weed scale",
    "cannabis accessories", "weed storage", "cannabis container", "pre-roll kit",
    "herb trimmer", "humidity packs"
]

# === Setup Google Sheets ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("google-credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_TAB)
existing = sheet.get_all_records()
existing_asins = {row["asin"] for row in existing if "asin" in row}

# === Helper for PAAPI Request ===
def sign_request(payload):
    method = "POST"
    endpoint = f"https://{MARKETPLACE}/paapi5/searchitems"
    host = MARKETPLACE
    uri = "/paapi5/searchitems"
    content_type = "application/json; charset=UTF-8"
    amz_target = "com.amazon.paapi5.v1.ProductAdvertisingAPIv1.SearchItems"
    t = time.gmtime()
    amz_date = time.strftime('%Y%m%dT%H%M%SZ', t)
    date_stamp = time.strftime('%Y%m%d', t)

    headers = {
        "content-encoding": "amz-1.0",
        "content-type": content_type,
        "host": host,
        "x-amz-date": amz_date,
        "x-amz-target": amz_target
    }

    canonical_headers = ''.join(f"{k}:{headers[k]}\n" for k in sorted(headers))
    signed_headers = ';'.join(sorted(headers))
    payload_hash = hashlib.sha256(payload.encode('utf-8')).hexdigest()
    canonical_request = f"{method}\n{uri}\n\n{canonical_headers}\n{signed_headers}\n{payload_hash}"

    algorithm = 'AWS4-HMAC-SHA256'
    credential_scope = f"{date_stamp}/{REGION}/ProductAdvertisingAPI/aws4_request"
    string_to_sign = f"{algorithm}\n{amz_date}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"

    def sign(key, msg): return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()
    k_date = sign(('AWS4' + AWS_SECRET_KEY).encode('utf-8'), date_stamp)
    k_region = sign(k_date, REGION)
    k_service = sign(k_region, "ProductAdvertisingAPI")
    k_signing = sign(k_service, "aws4_request")
    signature = hmac.new(k_signing, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

    authorization = (
        f"{algorithm} Credential={AWS_ACCESS_KEY}/{credential_scope}, "
        f"SignedHeaders={signed_headers}, Signature={signature}"
    )

    headers["Authorization"] = authorization
    return headers

# === Search Products and Update Sheet ===
new_rows = []

for keyword in KEYWORDS:
    print(f"🔍 Searching: {keyword}")
    body = {
        "Keywords": keyword,
        "SearchIndex": "All",
        "Resources": ["ItemInfo.Title"],
        "PartnerTag": ASSOCIATE_TAG,
        "PartnerType": "Associates",
        "Marketplace": "www.amazon.ca"
    }

    payload = json.dumps(body)
    headers = sign_request(payload)
    try:
        res = requests.post(f"https://{MARKETPLACE}/paapi5/searchitems", headers=headers, data=payload)
        res.raise_for_status()
        items = res.json().get("SearchResult", {}).get("Items", [])
        for item in items:
            asin = item.get("ASIN")
            title = item.get("ItemInfo", {}).get("Title", {}).get("DisplayValue", "")
            if asin and title and asin not in existing_asins:
                url = f"https://www.amazon.ca/dp/{asin}/?tag={ASSOCIATE_TAG}"
                new_rows.append([title, asin, keyword, url])
                existing_asins.add(asin)
    except Exception as e:
        print(f"❌ Failed: {e}")
    time.sleep(2)

if new_rows:
    sheet.append_rows(new_rows)
    print(f"✅ Appended {len(new_rows)} new products.")
else:
    print("⚠️ No new products found.")