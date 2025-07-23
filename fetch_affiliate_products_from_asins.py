#!/usr/bin/env python3
import time, datetime, hmac, hashlib, json, requests, gspread
from google.oauth2.service_account import Credentials

# === CONFIG ===
SHEET_ID      = "10RTloEY5nvjOBm7CaPhYMplxbY31Gf8CMVFkXVAW2to"
SHEET_TAB     = "AffiliateProducts"
GOOGLE_CRED   = "google-credentials.json"

ACCESS_KEY    = "AKPA76WINC1750936089"
SECRET_KEY    = "R27sm7NoWPzE+Zvftji0eBNMyNg1umtVNQOP9wux"
PARTNER_TAG   = "smarthomepu07-20"
REGION        = "us-east-1"
SERVICE       = "ProductAdvertisingAPI"
HOST          = "webservices.amazon.ca"
ENDPOINT      = f"https://{HOST}/paapi5/getitems"
MAX_PULLS     = 15  # daily rate limit guard
DELAY_SECONDS = 1.1

# 15 curated Canadian ASINs
ASINS = [
  "B08L8V7R5K","B07P1F6Y7D","B06XFG9N46","B07ZTCYRGR","B07JP61GNC",
  "B089KFG4R9","B00F30RYSQ","B08BLHLP6M","B071FSTJFT","B08L5SRN8V",
  "B07FDMCGC5","B07MMPZ32Y","B08S4V2Y5G","B07JKV5ZQW","B07XSJ1R2W"
]

# — Sheets setup —
scopes = ["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]
creds  = Credentials.from_service_account_file(GOOGLE_CRED, scopes=scopes)
gc     = gspread.authorize(creds)
ws     = gc.open_by_key(SHEET_ID).worksheet(SHEET_TAB)

def sign(key, msg):
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

def get_signature_key(key, date_stamp, region, service):
    k_date   = sign(("AWS4"+key).encode(), date_stamp)
    k_region = sign(k_date, region)
    k_service= sign(k_region, service)
    return sign(k_service, "aws4_request")

def fetch_item(asin):
    now        = datetime.datetime.utcnow()
    amz_date   = now.strftime("%Y%m%dT%H%M%SZ")
    date_stamp = now.strftime("%Y%m%d")

    payload = {
      "ItemIds": [asin],
      "Resources": ["ItemInfo.Title","DetailPageURL"],
      "PartnerTag": PARTNER_TAG,
      "PartnerType": "Associates",
      "Marketplace": "www.amazon.ca"
    }
    body = json.dumps(payload)
    # --- build signature ---
    canonical_uri      = "/paapi5/getitems"
    canonical_headers  = (
      f"content-encoding:amz-1.0\n"
      f"content-type:application/json; charset=UTF-8\n"
      f"host:{HOST}\n"
      f"x-amz-date:{amz_date}\n"
      f"x-amz-target:com.amazon.paapi5.v1.ProductAdvertisingAPIv1.GetItems\n"
    )
    signed_headers     = "content-encoding;content-type;host;x-amz-date;x-amz-target"
    payload_hash       = hashlib.sha256(body.encode()).hexdigest()
    canonical_request  = (
      f"POST\n{canonical_uri}\n\n"
      f"{canonical_headers}\n"
      f"{signed_headers}\n"
      f"{payload_hash}"
    )
    cred_scope         = f"{date_stamp}/{REGION}/{SERVICE}/aws4_request"
    string_to_sign     = (
      f"AWS4-HMAC-SHA256\n{amz_date}\n{cred_scope}\n"
      f"{hashlib.sha256(canonical_request.encode()).hexdigest()}"
    )
    signing_key        = get_signature_key(SECRET_KEY, date_stamp, REGION, SERVICE)
    signature          = hmac.new(signing_key, string_to_sign.encode(), hashlib.sha256).hexdigest()
    # --- headers ---
    auth_header = (
      f"AWS4-HMAC-SHA256 Credential={ACCESS_KEY}/{cred_scope}, "
      f"SignedHeaders={signed_headers}, Signature={signature}"
    )
    headers = {
      "Content-Encoding": "amz-1.0",
      "Content-Type":      "application/json; charset=UTF-8",
      "X-Amz-Date":        amz_date,
      "X-Amz-Target":      "com.amazon.paapi5.v1.ProductAdvertisingAPIv1.GetItems",
      "Authorization":     auth_header,
      "Host":              HOST
    }
    # --- call API ---
    r = requests.post(ENDPOINT, headers=headers, data=body)
    if r.status_code!=200:
        print(f"❌ {asin} → {r.status_code}: {r.text}")
        return None
    js = r.json().get("ItemsResult",{})
    items = js.get("Items",[])
    if not items:
        print(f"⚠️ {asin} → no items")
        return None
    item = items[0]
    title = item["ItemInfo"]["Title"]["DisplayValue"]
    url   = item["DetailPageURL"]
    return title, url

def main():
    print(f"🔗 Fetching up to {MAX_PULLS} items…")
    added = 0
    existing = {r[0] for r in ws.get_all_values()[1:]}
    for asin in ASINS:
        if added>=MAX_PULLS: break
        res = fetch_item(asin)
        if not res: 
            time.sleep(DELAY_SECONDS)
            continue
        title, url = res
        if title in existing:
            print(f"↪️  Skip duplicate: {title}")
        else:
            # append [Product Name, ASIN, URL, DatePulled]
            ws.append_row([title, asin, url, datetime.datetime.utcnow().isoformat()])
            print(f"✅ Added: {title}")
            added +=1
        time.sleep(DELAY_SECONDS)
    print("🎉 Done.")

if __name__=="__main__":
    main()
