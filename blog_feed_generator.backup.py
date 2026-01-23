#!/usr/bin/env python3
import os, datetime, pathlib, re
from bs4 import BeautifulSoup

POSTS_DIR_PRIMARY = "posts_wrapped"
POSTS_DIR_FALLBACK= "posts"
FEED_FILE         = "blog-feed.html"
MAX_POSTS         = 60

STYLE = """
*{box-sizing:border-box}
body{margin:0;background:#d2ae8a;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Inter,Arial}
h1{font-size:clamp(32px,4vw,54px);margin:0;padding:32px}
.grid{display:grid;gap:22px;padding:0 22px 32px;grid-template-columns:repeat(auto-fill,minmax(320px,1fr))}
.card{border-radius:18px;overflow:hidden;background:#111;color:#fff;box-shadow:0 6px 24px rgb(0 0 0 / 25%)}
.card a{color:inherit;text-decoration:none}
.thumb{width:100%;height:220px;object-fit:cover;display:block;background:#222}
.meta{padding:18px}
.title{font-size:clamp(18px,2.2vw,24px);line-height:1.2;margin:0 0 6px}
.date{opacity:.75;font-size:14px;margin:0}
"""

SUFFIX_RE = re.compile(r"\s*\|\s*Reserved Cannabis Blog$", re.I)

def first_image_src(soup:BeautifulSoup)->str:
    img = soup.find("img")
    return img["src"] if img and img.has_attr("src") else ""

def clean_title(text:str)->str:
    t = SUFFIX_RE.sub("", text or "").strip()
    return t

def title_of(soup:BeautifulSoup, fallback:str)->str:
    # prefer <h1> (clean)
    h1 = soup.find("h1")
    if h1:
        return clean_title(h1.get_text(strip=True))
    # fallback to <title> (clean)
    if soup.title and soup.title.string:
        return clean_title(soup.title.string.strip())
    return fallback

def date_of(soup:BeautifulSoup, path:str)->str:
    t = soup.find("time")
    if t:
        txt = (t.get_text() or "").strip()
        if txt:
            return txt
        dt = t.get("datetime")
        if dt:
            try:
                d = datetime.datetime.fromisoformat(dt.replace("Z","+00:00"))
                return d.strftime("%b %d, %Y")
            except:
                pass
    ts = os.path.getmtime(path)
    return datetime.datetime.utcfromtimestamp(ts).strftime("%b %d, %Y")

def pick_posts_dir():
    return POSTS_DIR_PRIMARY if os.path.isdir(POSTS_DIR_PRIMARY) else POSTS_DIR_FALLBACK

def main():
    posts_dir = pick_posts_dir()
    items = []
    for name in sorted(os.listdir(posts_dir), reverse=True):
        if not name.endswith(".html"):
            continue
        path = os.path.join(posts_dir, name)
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
        items.append({
            "href": f"{posts_dir}/{name}",
            "img" : first_image_src(soup),
            "title": title_of(soup, pathlib.Path(name).stem.replace("-", " ").title()),
            "date": date_of(soup, path),
        })
    items = items[:MAX_POSTS]

    cards = []
    for it in items:
        img = f'<img class="thumb" src="{it["img"]}" alt="">' if it["img"] else '<div class="thumb"></div>'
        cards.append(f"""
        <article class="card">
          <a href="{it['href']}" target="_blank" rel="noopener">
            {img}
            <div class="meta">
              <h2 class="title">{it['title']}</h2>
              <p class="date">{it['date']}</p>
            </div>
          </a>
        </article>""")

    html = f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Reserved Cannabis Blog</title>
<style>{STYLE}</style>
</head><body>
<h1>Latest Articles</h1>
<section class="grid">
{''.join(cards)}
</section>
</body></html>"""
    with open(FEED_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ Blog feed generated: {FEED_FILE} with {len(items)} post(s)")

if __name__ == "__main__":
    main()
