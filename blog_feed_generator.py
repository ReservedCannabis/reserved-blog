#!/usr/bin/env python3
import os, glob, re
from datetime import datetime

# ──────────────────────────────────────────────────────────────────────────────
#              ← Change this if you ever move your blog to another domain! →
BASE_URL  = "https://blog.reservedcannabis.ca"
POSTS_DIR = "posts"
OUTPUT    = "blog-feed.html"
# ──────────────────────────────────────────────────────────────────────────────

def extract_title(path):
    """Find the first <h1>…</h1> in the file for a human-friendly title."""
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = re.search(r"<h1[^>]*>([^<]+)</h1>", line)
            if m:
                return m.group(1).strip()
    # fallback to filename
    return os.path.splitext(os.path.basename(path))[0].replace("-", " ").title()

def main():
    # 1) Gather all .html files in posts/
    files = glob.glob(os.path.join(POSTS_DIR, "*.html"))
    posts = []
    for fn in files:
        # slug.html → slug
        slug = os.path.basename(fn)
        # last-modified timestamp
        ts   = os.path.getmtime(fn)
        posts.append((ts, slug, extract_title(fn)))
    # 2) Sort newest first
    posts.sort(reverse=True, key=lambda x: x[0])

    # 3) Build HTML
    lines = [
        "<!doctype html>",
        "<html lang=\"en\">",
        "<head>",
        "  <meta charset=\"utf-8\">",
        f"  <title>Cannabis Blog – Reserved Cannabis</title>",
        "  <style>",
        "    body { max-width: 720px; margin: 2em auto; font-family: system-ui; background: #d0b08b; }",
        "    h1 { font-size: 2rem; }",
        "    ul { list-style: none; padding: 0; }",
        "    li { margin: 1em 0; padding: 1em; background: white; border-radius: .5em; }",
        "    a { text-decoration: none; color: #333; font-weight: bold; font-size: 1.2rem; }",
        "    .date { display: block; color: gray; margin-top: .25em; font-size: .9rem; }",
        "  </style>",
        "</head>",
        "<body>",
        "  <h1>Latest Articles</h1>",
        "  <ul>",
    ]

    for ts, slug, title in posts:
        url  = f"{BASE_URL}/{POSTS_DIR}/{slug}"
        date = datetime.fromtimestamp(ts).strftime("%b %-d, %Y")
        lines.append(f'    <li>')
        lines.append(f'      <a href="{url}">{title}</a>')
        lines.append(f'      <span class="date">{date}</span>')
        lines.append(f'    </li>')

    lines.extend([
        "  </ul>",
        "</body>",
        "</html>",
    ])

    with open(OUTPUT, "w", encoding="utf-8") as out:
        out.write("\n".join(lines))

if __name__ == "__main__":
    main()
