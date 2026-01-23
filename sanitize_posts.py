import os, re, glob
from bs4 import BeautifulSoup

POST_DIRS = ["posts", "posts_wrapped"]
MARKER = "FEATURED_IMAGE_INSERTED"
IMG_RE = re.compile(r"<img\b[^>]*>", re.I)

def fix_link(a):
    href = (a.get("href") or "").lower()
    if "amazon." in href:
        a["target"] = "_blank"
        rel = (a.get("rel") or []) + ["nofollow","sponsored","noopener"]
        a["rel"] = " ".join(sorted(set(rel)))

def sanitize_file(fp):
    with open(fp, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")

    # 1) Capture featured image src if we have one already
    featured_src = None
    # Heuristic: first <img> closest to our marker comment, else first <img> in doc
    comments = soup.find_all(string=lambda x: isinstance(x, type(soup.original_encoding)) and False)
    # BeautifulSoup comments type trick is messy; fallback: search raw
    marker_pos = html.find(MARKER)
    if marker_pos >= 0:
        # Look for the first <img> after marker in raw text
        after = html[marker_pos:]
        m = IMG_RE.search(after)
        if m:
            # Parse that snippet to extract src
            frag = BeautifulSoup(m.group(0), "html.parser")
            im = frag.find("img")
            if im and im.get("src"):
                featured_src = im["src"]

    if not featured_src:
        img = soup.find("img")
        if img and img.get("src"):
            featured_src = img["src"]

    # 2) Drop ALL <img> tags from content
    for img in soup.find_all("img"):
        img.decompose()

    # 3) Find marker location and insert exactly one featured image
    if MARKER in html and featured_src:
        # Replace marker comment or marker text with a clean img tag
        repl = f'<!-- {MARKER} --><img src="{featured_src}" alt="" style="max-width:100%;height:auto;display:block;margin:1.5rem 0;">'
        html = re.sub(rf"<!--\s*{MARKER}\s*-->|{MARKER}", repl, html, count=1, flags=re.I)
    else:
        # If no marker, prepend a single image at top of article
        if featured_src:
            body = soup.find("main") or soup.body or soup
            body.insert(0, soup.new_tag("img", src=featured_src, **{"style":"max-width:100%;height:auto;display:block;margin:1.5rem 0;"}))
            html = str(soup)

    # 4) Fix Amazon links
    soup2 = BeautifulSoup(html, "html.parser")
    for a in soup2.find_all("a"):
        fix_link(a)

    with open(fp, "w", encoding="utf-8") as f:
        f.write(str(soup2))

def run():
    changed = 0
    for d in POST_DIRS:
        if not os.path.isdir(d):
            continue
        for fp in glob.glob(os.path.join(d, "*.html")):
            sanitize_file(fp)
            changed += 1
    print(f"Sanitized {changed} file(s). Only one featured image will remain per post.")

if __name__ == "__main__":
    run()
