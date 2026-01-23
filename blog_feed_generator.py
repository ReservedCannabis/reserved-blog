#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import re, datetime

POST_DIRS = [Path("posts_wrapped"), Path("posts")]
OUT_HTML  = Path("blog-feed.html")

def utcts(ts: float) -> str:
    # Human date for card
    return datetime.datetime.fromtimestamp(ts, datetime.UTC).strftime("%b %d, %Y")

def extract_title(html: str, fallback: str) -> str:
    m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.I | re.S)
    if m:
        return re.sub(r"\s+", " ", m.group(1)).strip()
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
    if m:
        return re.sub(r"\s+", " ", m.group(1)).strip()
    return fallback

def extract_og_image(html: str) -> str | None:
    m = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', html, re.I)
    return m.group(1) if m else None

def extract_first_img(html: str) -> str | None:
    m = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', html, re.I)
    return m.group(1) if m else None

PLACEHOLDER = "https://dummyimage.com/1200x630/202020/ffffff.png&text=Reserved+Cannabis"

def first_image_url(html: str) -> str:
    return extract_og_image(html) or extract_first_img(html) or PLACEHOLDER

def collect_posts():
    items = []
    seen = set()
    for root in POST_DIRS:
        if not root.exists():
            continue
        for fp in root.glob("*.html"):
            slug = fp.name
            if slug in seen:  # prefer wrapped versions
                continue
            html = fp.read_text(encoding="utf-8", errors="ignore")
            title = extract_title(html, fp.stem.replace("-", " ").title())
            img = first_image_url(html)
            ts  = fp.stat().st_mtime
            items.append((ts, fp, title, img))
            seen.add(slug)
    # newest first
    items.sort(key=lambda x: x[0], reverse=True)
    return items

CARD = """<a class="card" href="{href}">
  <img alt="{title}" src="{img}">
  <div class="meta">
    <h3>{title}</h3>
    <p class="date">{date}</p>
  </div>
</a>"""

SHELL = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>Reserved Cannabis — Latest Articles</title>
<meta name="viewport" content="width=device-width,initial-scale=1" />
<style>
  body{{margin:0;background:#caa986;font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif}}
  main{{max-width:1200px;margin:40px auto;padding:0 16px}}
  h1{{font-size:40px;margin:0 0 20px}}
  .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:18px}}
  .card{{display:block;border-radius:16px;overflow:hidden;background:#fff;text-decoration:none;color:#111;box-shadow:0 6px 20px rgba(0,0,0,.1)}}
  .card img{{width:100%;height:180px;object-fit:cover;display:block;background:#e9e9e9}}
  .meta{{padding:14px}}
  .meta h3{{margin:0 0 8px;font-size:20px;line-height:1.25}}
  .meta .date{{margin:0;color:#666;font-size:14px}}
</style>
</head>
<body>
  <main>
    <h1>Reserved Cannabis — Latest Articles</h1>
    <div class="grid">
      {cards}
    </div>
  </main>
</body>
</html>"""

def main():
    posts = collect_posts()
    cards = []
    for ts, fp, title, img in posts:
        href = f"posts/{fp.name}"
        cards.append(CARD.format(href=href, img=img, title=title, date=utcts(ts)))
    OUT_HTML.write_text(SHELL.format(cards="\n".join(cards)), encoding="utf-8")
    print(f"✅ Blog feed generated: {OUT_HTML} with {len(posts)} post(s)")

if __name__ == "__main__":
    main()
