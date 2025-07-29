#!/usr/bin/env python3
import glob, os
from datetime import datetime
from bs4 import BeautifulSoup

POST_DIR = "posts"
OUTPUT   = "blog-feed.html"

# 1) find all posts
paths = glob.glob(f"{POST_DIR}/*.html")

# 2) build (mtime, title, url, date) tuples
entries = []
for p in paths:
    mtime = os.path.getmtime(p)
    date  = datetime.fromtimestamp(mtime).strftime("%b %d, %Y")
    with open(p, encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
        raw  = soup.title.string or ""
    # strip any leading "Reserved Cannabis – "
    if "–" in raw:
        title = raw.split("–", 1)[1].strip()
    else:
        title = raw.strip()
    url = f"{POST_DIR}/{os.path.basename(p)}"
    entries.append((mtime, title, url, date))

# 3) sort newest first
entries.sort(key=lambda e: e[0], reverse=True)

# 4) write out blog-feed.html
with open(OUTPUT, "w", encoding="utf-8") as out:
    out.write("""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Latest Articles</title>
</head>
<body>
  <h1>Latest Articles</h1>
  <ul>
""")
    for _, title, url, date in entries:
        out.write(f'    <li><a href="{url}">{title}</a> ({date})</li>\n')
    out.write("""  </ul>
</body>
</html>
""")
print(f"✅ Wrote {OUTPUT} with {len(entries)} entries")

if __name__ == '__main__':
    main()