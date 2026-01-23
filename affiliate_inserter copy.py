#!/usr/bin/env python3
import os, random
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ── CONFIG ───────────────────────────────────────────────────────────────
SHEET_ID = "10RTloEY5nvjOBm7CaPhYMplxbY31Gf8CMVFkXVAW2to"
TAB     = "AffiliateProducts"
# ──────────────────────────────────────────────────────────────────────────

# 1) auth
scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("google-credentials.json", scope)
gc = gspread.authorize(creds)
ws = gc.open_by_key(SHEET_ID).worksheet(TAB)

# 2) grab the full sheet as rows
all_vals = ws.get_all_values()
if not all_vals or len(all_vals) < 2:
    print("⚠️ Sheet is empty or missing data.")
    exit(1)

header = all_vals[0]
rows   = all_vals[1:]

# 3) locate our three columns
try:
    idx_name = header.index("product_name")
    idx_asin = header.index("asin")
    idx_link = header.index("link")
except ValueError as e:
    print("❌ Cannot find column:", e)
    print("   Header row is:", header)
    exit(1)

# 4) build product list
prods = []
for r in rows:
    name = r[idx_name].strip()
    asin = r[idx_asin].strip()
    link = r[idx_link].strip()
    if name and asin and link:
        prods.append((name, link))

if not prods:
    print("⚠️ No fully-populated rows (name+asin+link).")
    exit(0)

# 5) inject into posts
post_files = sorted(f for f in os.listdir("posts") if f.endswith(".html"))
random.shuffle(prods)

injected = 0
for post, (name, link) in zip(post_files, prods):
    path = os.path.join("posts", post)
    html = open(path).read()

    if link in html:
        continue

    snippet = (
        f'<p style="margin-top:20px;">'
        f'<strong>Featured Product:</strong> '
        f'<a href="{link}" target="_blank" rel="noopener noreferrer">{name}</a>'
        f' – A top-rated cannabis accessory on Amazon Canada.'
        f'</p>'
    )
    new_html = html.replace("</body>", snippet + "\n</body>")

    with open(path, "w") as f:
        f.write(new_html)

    print(f"✅ Injected {name} → {post}")
    injected += 1

print(f"\n✅ Done! {injected} inserted, {len(post_files)-injected} skipped.")