#!/usr/bin/env python3
import os, time, datetime, hmac, hashlib, json, requests
import gspread
from google.oauth2.service_account import Credentials

# === CONFIG ===
GOOGLE_CRED   = "google-credentials.json"
SHEET_ID      = "10RTloEY5nvjOBm7CaPhYMplxbY31Gf8CMVFkXVAW2to"
ASIN_TAB      = "AffiliateProducts"
PRODUCT_TAB   = "AffiliateProducts"
ACCESS_KEY    = "AKPA76WINC1750936089"
SECRET_KEY    = "R27sm7NoWPzE+Zvftji0eBNMyNg1umtVNQOP9wux"
PARTNER_TAG   = "smarthomepu07-20"
REGION        = "us-east-1"
SERVICE       = "ProductAdvertisingAPI"
HOST          = "webservices.amazon.ca"
ENDPOINT      = f"https://{HOST}/paapi5/getitems"
MAX_DAILY     = 15
DELAY_SECONDS = 1.1

# ── Sheets setup ─────────────────────────────────────────────────
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds   = Credentials.from_service_account_file(GOOGLE_CRED, scopes=scopes)
client  = gspread.authorize(creds)
doc     = client.open_by_key(SHEET_ID)
asin_ws = doc.worksheet(ASIN_TAB)
prod_ws = doc.worksheet(PRODUCT_TAB)

# ── HMAC signing helpers ─────────────────────────────────────────
def _sign(key, msg):
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

def get_signature_key(key, date_stamp, region, service):
    k_date   = _sign(("AWS4" + key).encode(), date_stamp)
    k_region = _sign(k_date, region)
    k_service= _sign(k_region, service)
    k_sign   = _sign(k_service, "aws4_request")
    return k_sign

# ── Load pending ASINs ───────────────────────────────────────────
rows = asin_ws.get_all_values()[1:]
pending = []
for idx, row in enumerate(rows, start=2):
    asin = row[0].strip()
    status = row[2].strip().lower() if len(row)>2 else ""
    if asin and status != "done":
        pending.append((idx, asin))
if not pending:
    print("⚠️ No new ASINs to process.")
    exit()

print(f"🔎 {len(pending)} ASIN(s) pending, processing up to {MAX_DAILY}…")
existing = {r[0] for r in prod_ws.get_all_values()[1:]}

added = 0
for row_num, asin in pending:
    if added >= MAX_DAILY:
        break

    # timestamp for signing
    now        = datetime.datetime.utcnow()
    amz_date   = now.strftime("%Y%m%dT%H%M%SZ")
    date_stamp = now.strftime("%Y%m%d")

    # build PA-API payload
    payload = {
        "ItemIds": [asin],
        "Resources": [
            "ItemInfo.Title",
            "Offers.Listings.Price",
            "Images.Primary.Large",
            "DetailPageURL"
        ],
        "PartnerTag": PARTNER_TAG,
        "PartnerType": "Associates",
        "Marketplace": "www.amazon.ca"
    }
    body = json.dumps(payload)
    
    # canonical request
    canonical_uri       = "/paapi5/getitems"
    canonical_headers   = (
        f"content-encoding:amz-1.0\n"
        f"content-type:application/json; charset=UTF-8\n"
        f"host:{HOST}\n"
        f"x-amz-date:{amz_date}\n"
        f"x-amz-target:com.amazon.paapi5.v1.ProductAdvertisingAPIv1.GetItems\n"
    )
    signed_headers      = "content-encoding;content-type;host;x-amz-date;x-amz-target"
    payload_hash        = hashlib.sha256(body.encode()).hexdigest()
    canonical_request   = (
        f"POST\n{canonical_uri}\n\n"
        f"{canonical_headers}\n"
        f"{signed_headers}\n"
        f"{payload_hash}"
    )
    
    # string to sign
    credential_scope = f"{date_stamp}/{REGION}/{SERVICE}/aws4_request"
    string_to_sign   = (
        f"AWS4-HMAC-SHA256\n"
        f"{amz_date}\n"
        f"{credential_scope}\n"
        f"{hashlib.sha256(canonical_request.encode()).hexdigest()}"
    )
    signing_key = get_signature_key(SECRET_KEY, date_stamp, REGION, SERVICE)
    signature   = hmac.new(signing_key, string_to_sign.encode(), hashlib.sha256).hexdigest()
    auth_header = (
        f"AWS4-HMAC-SHA256 Credential={ACCESS_KEY}/{credential_scope}, "
        f"SignedHeaders={signed_headers}, Signature={signature}"
    )

    headers = {
        "Content-Encoding": "amz-1.0",
        "Content-Type":      "application/json; charset=UTF-8",
        "Host":              HOST,
        "X-Amz-Date":        amz_date,
        "X-Amz-Target":      "com.amazon.paapi5.v1.ProductAdvertisingAPIv1.GetItems",
        "Authorization":     auth_header
    }

    print(f"📡 Fetching {asin} …", end=" ")
    resp = requests.post(ENDPOINT, headers=headers, data=body, timeout=10)
    print(f"Status {resp.status_code}")
    if resp.status_code != 200:
        print("   ", resp.text)
        continue

    data  = resp.json().get("ItemsResult",{}).get("Items",[])
    if not data:
        print("   No items returned.")
        continue

    itm    = data[0]
    title  = itm["ItemInfo"]["Title"]["DisplayValue"]
    price  = itm["Offers"]["Listings"][0]["Price"]["DisplayAmount"]
    image  = itm["Images"]["Primary"]["Large"]["URL"]
    url    = itm["DetailPageURL"]
    key    = (title.strip(), asin)

    # skip duplicate
    if title in existing:
        asin_ws.update_cell(row_num, 3, "Done")
        print("   ⚠️ Duplicate, skipped.")
    else:
        prod_ws.append_row([title, asin, url, image, price])
        asin_ws.update_cell(row_num, 3, "Done")
        print("   ✅ Added.")

        added += 1
        time.sleep(DELAY_SECONDS)

print(f"🏁 Done — {added} new product(s) fetched.")
