#!/usr/bin/env python3
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ── CONFIG ───────────────────────────────────────────────────────────────
SHEET_ID   = "10RTloEY5nvjOBm7CaPhYMplxbY31Gf8CMVFkXVAW2to"
TAB_NAME   = "AffiliateProducts"
AFF_TAG    = "smarthomepu07-20"
# ──────────────────────────────────────────────────────────────────────────

# 1) auth
scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("google-credentials.json", scope)
client = gspread.authorize(creds)

# 2) open sheet & tab
sh = client.open_by_key(SHEET_ID)
ws = sh.worksheet(TAB_NAME)

# 3) read all rows (incl. header)
rows = ws.get_all_values()
header = rows.pop(0)
# find the column indices
asin_col = header.index("asin") + 1
link_col = header.index("link") + 1

# 4) for each data row: build link and write it back
updates = []
for i, row in enumerate(rows, start=2):
    asin = row[asin_col-1].strip()
    if not asin:
        continue

    url = f"https://www.amazon.ca/gp/product/{asin}/?tag={AFF_TAG}"
    updates.append({'range': gspread.utils.rowcol_to_a1(i, link_col),
                    'values': [[url]]})

if updates:
    ws.batch_update(updates)
    print(f"✅ Populated {len(updates)} Amazon.ca links with tag into column ‘link’")
else:
    print("⚠️ No ASINs found to populate.")