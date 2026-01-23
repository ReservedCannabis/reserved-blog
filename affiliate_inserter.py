import os, glob, re
from pathlib import Path
from bs4 import BeautifulSoup

SHEET_ID    = os.environ.get("AFFIL_SHEET_ID", "").strip()
SHEET_RANGE = os.environ.get("AFFIL_SHEET_RANGE", "AffiliateProducts!A:C").strip()
CREDS       = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "google-credentials.json")

POSTS_DIR   = "posts_wrapped" if Path("posts_wrapped").exists() else "posts"

BOX_START = "<!-- AFFIL_BOX_START -->"
BOX_END   = "<!-- AFFIL_BOX_END -->"

def normalize_cols(row):
    return { (k or "").strip().lower(): v for k,v in row.items() }

def _uniquify_headers(headers):
    seen = {}
    out = []
    for h in headers:
        key = (h or "").strip()
        if key == "":
            key = "col"
        base = key
        i = 1
        while key.lower() in seen:
            i += 1
            key = f"{base}_{i}"
        seen[key.lower()] = True
        out.append(key)
    return out

def _sheet_rows_via_values():
    import gspread
    gc = gspread.service_account(filename=CREDS)
    ws = gc.open_by_key(SHEET_ID).worksheet(SHEET_RANGE.split('!')[0])
    vals = ws.get_all_values()
    if not vals:
        return []
    headers = _uniquify_headers(vals[0])
    rows = []
    for r in vals[1:]:
        row = {}
        for i, h in enumerate(headers):
            row[h] = r[i] if i < len(r) else ""
        rows.append(row)
    return rows

def fetch_products():
    rows = []
    # Try Google Sheet first
    if SHEET_ID and Path(CREDS).exists():
        try:
            rows = _sheet_rows_via_values()
            print(f"✅ Loaded {len(rows)} rows from Google Sheet.")
        except Exception as e:
            print(f"⚠️  Sheet read failed: {e}")

    # Fallback to CSV if present
    if not rows and Path("affiliate_products.csv").exists():
        import csv
        with open("affiliate_products.csv", newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        print(f"✅ Loaded {len(rows)} rows from affiliate_products.csv")

    # Normalize + filter to rows that have a link and name
    norm = []
    for r in rows:
        rr = normalize_cols(r)
        link = rr.get("link") or rr.get("url") or ""
        name = rr.get("product_name") or rr.get("name") or ""
        if link and name:
            norm.append({"name": name, "link": link})
    return norm

def build_box(products):
    items = []
    for p in products:
        href = p["link"].replace("&amp;", "&").strip()
        if href.startswith("www.amazon."):
            href = "https://" + href
        items.append(f'<li><a href="{href}" target="_blank" rel="nofollow noopener noreferrer">{p["name"]}</a></li>')
    if not items:
        return ""
    return (
f"""{BOX_START}
<div class="aff-box" style="background:#111;color:#eee;padding:1rem;border-radius:12px;margin:1.5rem 0;">
  <div style="font-weight:600;margin-bottom:.5rem;">Recommended accessories</div>
  <ul style="margin:0 0 0 1rem;padding:0;line-height:1.7;">
    {''.join(items)}
  </ul>
</div>
{BOX_END}
""".strip()
    )

def inject_box(html, box_html):
    if not box_html:
        return html, False
    # Idempotent: remove any previous box first
    html = re.sub(re.compile(re.escape(BOX_START)+r".*?"+re.escape(BOX_END), re.S), "", html)
    soup = BeautifulSoup(html, "html.parser")
    body = soup.body or soup
    h1 = body.find("h1")
    target = h1.parent if h1 and h1.parent else body
    frag = BeautifulSoup(box_html, "html.parser")
    target.insert(1, frag)
    return str(soup), True

def main():
    products = fetch_products()
    if not products:
        print("⚠️  No affiliate products found (Sheet or CSV). Skipping.")
        return
    products = products[:5]  # keep the box tidy
    box_html = build_box(products)

    changed = 0
    for fp in sorted(Path(POSTS_DIR).glob("*.html")):
        html = fp.read_text(encoding="utf-8")
        new_html, did = inject_box(html, box_html)
        if did and new_html != html:
            fp.write_text(new_html, encoding="utf-8")
            changed += 1
    print(f"✅ Affiliate boxes injected into {changed} post(s)")

if __name__ == "__main__":
    main()
