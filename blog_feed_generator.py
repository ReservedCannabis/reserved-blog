#!/usr/bin/env python3
import os, re, json
from datetime import datetime
from pathlib import Path

POST_DIR   = Path("posts")
LIST_FILE  = "blog-feed.html"
DATE_STORE = ".article_dates.json"

# load or init
if Path(DATE_STORE).exists():
    article_dates = json.loads(Path(DATE_STORE).read_text())
else:
    article_dates = {}

entries = []
for html_path in sorted(POST_DIR.glob("*.html")):
    content = html_path.read_text()
    slug    = html_path.stem

    # get published date from comment
    m = re.search(r"<!--\s*published:([\d\-]+)\s*-->", content)
    date = m.group(1) if m else datetime.utcnow().strftime("%Y-%m-%d")

    # preserve old date if exists
    if slug in article_dates:
        date = article_dates[slug]
    else:
        article_dates[slug] = date

    # title
    m2 = re.search(r"<h1>(.*?)</h1>", content, re.S)
    title = m2.group(1).strip() if m2 else slug.replace("_"," ").title()

    # summary
    m3 = re.search(r"<p>(.*?)</p>", content, re.S)
    summary = m3.group(1).strip() if m3 else ""

    # first image
    m4 = re.search(r'<img[^>]+src="([^"]+)"', content)
    img = m4.group(1) if m4 else ""

    entries.append({
        "slug": slug,
        "title": title,
        "date": date,
        "summary": summary,
        "img": img
    })

# save back the date map
Path(DATE_STORE).write_text(json.dumps(article_dates, indent=2))

# build listing HTML
out = ["<!DOCTYPE html>",
       "<html lang='en'><head><meta charset='UTF-8'>",
       "<title>Reserved Cannabis Blog</title>",
       "<style>body{background:#111;color:#fff;font-family:Arial,sans-serif;padding:40px;}"+
       ".post{margin-bottom:40px;}a{color:#ffc107;text-decoration:none;}a:hover{text-decoration:underline;}"+
       "img{max-width:100%;display:block;margin-bottom:10px;}"+
       "h2{margin:0;}small{color:#aaa;}"+
       "</style></head><body>",
       "<h1>Educational Cannabis Articles</h1>"
]

# newest first
for e in sorted(entries, key=lambda x: x["date"], reverse=True):
    out.append("<div class='post'>")
    if e["img"]:
        out.append(f"<a href='{e['slug']}.html'><img src='{e['img']}' alt=''></a>")
    out.append(f"<h2><a href='{e['slug']}.html'>{e['title']}</a></h2>")
    out.append(f"<small>{e['date']}</small>")
    out.append(f"<p>{e['summary']}</p>")
    out.append("</div>")

out.append("</body></html>")
Path(LIST_FILE).write_text("\n".join(out))
print("✅", LIST_FILE, "written with", len(entries), "posts.")