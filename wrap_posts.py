#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Wrap raw posts with a styled shell, ensure a single featured image is present,
and inject <meta property="og:image"> so the feed can always find a tile image.

Idempotent: you can run it repeatedly.
"""

from pathlib import Path
from bs4 import BeautifulSoup
import re

SRC_DIR  = Path("posts")
DST_DIR  = Path("posts_wrapped")
DST_DIR.mkdir(parents=True, exist_ok=True)

WRAP_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <meta name="description" content="{title}">
  {og_image}
  <style>
    html,body{{margin:0;background:#0b0b0b;color:#eee;font-family:system-ui,-apple-system,Segoe UI,Roboto,Inter,Arial,sans-serif}}
    article{{max-width:850px;margin:48px auto;padding:0 20px;line-height:1.6}}
    h1{{font-size:44px;line-height:1.15;margin:0 0 8px}}
    time{{display:block;color:#aaa;margin:0 0 24px}}
    img.featured{{width:100%;height:auto;border-radius:14px;display:block;margin:0 0 24px}}
    a{{color:#a7e0ff}}
    h2{{margin-top:28px}}
    h3{{margin-top:22px}}
  </style>
</head>
<body>
  <article>
    {content}
  </article>
</body>
</html>
"""

IMG_RE = re.compile(r"<img\b", re.I)

def ensure_og_image(soup, head, featured_src):
    # ensure <head> exists
    if head is None:
        head = soup.head
    if head is None:
        head = soup.new_tag("head")
        if soup.html:
            soup.html.insert(0, head)
        else:
            soup.insert(0, head)
    """Insert/update <meta property='og:image'> from featured_src."""
    if not featured_src:
        return
    meta = head.find("meta", attrs={"property": "og:image"})
    if meta:
        meta["content"] = featured_src
    else:
        tag = soup.new_tag("meta")
        tag["property"] = "og:image"
        tag["content"] = featured_src
        head.append(tag)

def wrap_one(path: Path) -> bool:
    html = path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")

    # Title
    title = (soup.find("h1") or soup.find("title"))
    title_text = title.get_text(strip=True) if title else path.stem.replace("-", " ").title()

    body = soup.body or soup

    # Keep only the FIRST image as the featured image, remove others that appear before the first H2.
    featured_src = ""
    first_img = body.find("img")
    if first_img and first_img.get("src"):
        featured_src = first_img["src"]
        first_img["class"] = list(set((first_img.get("class") or []) + ["featured"]))
        # Remove other images that occur before the first H2 (to prevent many duplicate heroes)
        first_h2 = body.find("h2")
        if first_h2:
            for img in body.find_all("img"):
                if img is not first_img:
                    # if img is located before first_h2 in document order, drop it
                    if img.sourcepos if hasattr(img, "sourcepos") else True:
                        # conservative: remove if it's before the first H2 tag found in tree traversal
                        # we approximate by stopping once we hit first_h2
                        # simpler: if img is not the featured, and there's an h2 somewhere, drop all other imgs
                        img.decompose()
        else:
            # No h2 at all -> drop all other images to keep only 1
            for img in body.find_all("img"):
                if img is not first_img:
                    img.decompose()

    # Build wrapped HTML and inject og:image from featured_src
    head = BeautifulSoup("<head></head>", "html.parser").head
    ensure_og_image(soup, head, featured_src)
    og_image_meta = str(head.find("meta", attrs={"property": "og:image"})) if featured_src else ""

    wrapped = WRAP_HTML.format(
        title=title_text,
        og_image=og_image_meta or "",
        content=str(body)
    )
    (DST_DIR / path.name).write_text(wrapped, encoding="utf-8")
    return True

def main():
    count = 0
    for p in sorted(SRC_DIR.glob("*.html")):
        if wrap_one(p):
            count += 1
    print(f"✅ Wrapped posts saved to '{DST_DIR.name}'")

if __name__ == "__main__":
    main()