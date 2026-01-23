# ===============================
# rss_generator.py  (Full file)
# ===============================
import os, datetime
from bs4 import BeautifulSoup

POSTS_DIR   = "posts_wrapped"
OUTPUT_FILE = "rss.xml"
BASE_URL    = "https://reservedcannabis.github.io/reserved-blog"  # adjust if repo path differs

items = []
for filename in os.listdir(POSTS_DIR):
    if not filename.endswith(".html"): continue
    filepath = os.path.join(POSTS_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    title_tag = soup.find("h1")
    title = title_tag.get_text(strip=True) if title_tag else "Untitled"
    first_p = soup.find("p")
    desc = first_p.get_text(strip=True) if first_p else title
    mtime = os.path.getmtime(filepath)
    pub = datetime.datetime.fromtimestamp(mtime, datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    link = f"{BASE_URL}/posts_wrapped/{filename}"
    items.append(f"""
    <item>
      <title>{title}</title>
      <link>{link}</link>
      <description>{desc}</description>
      <pubDate>{pub}</pubDate>
      <guid isPermaLink="true">{link}</guid>
    </item>""")

rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Reserved Cannabis Blog</title>
    <link>{BASE_URL}/</link>
    <description>Latest cannabis articles and tips</description>
    {''.join(items)}
  </channel>
</rss>
"""

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(rss)

print(f"✅ RSS feed generated: {OUTPUT_FILE} with {len(items)} item(s)")
