#!/usr/bin/env python3
import os
from pathlib import Path

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Reserved Cannabis – {title}</title>
  <meta name="description" content="{summary}">
  <style>
    body {{ background: #111; color: #fff; font-family: Arial, sans-serif; padding: 40px; }}
    a {{ color: #ffc107; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    img {{ max-width: 100%; margin-bottom: 20px; }}
  </style>
</head>
<body>
{body}
</body>
</html>"""

def extract_meta(html: str):
    # first <h1> text
    import re
    m = re.search(r"<h1>(.*?)</h1>", html, re.S)
    title   = m.group(1).strip() if m else "Reserved Cannabis"
    # first paragraph as summary
    m2 = re.search(r"<p>(.*?)</p>", html, re.S)
    summary = m2.group(1).strip() if m2 else title
    return title, summary

def main():
    posts = Path("posts").glob("*.html")
    for path in posts:
        txt = path.read_text()
        title, summary = extract_meta(txt)
        # remove any target="_blank" on internal links
        txt = txt.replace(" target=\"_blank\"", "")
        wrapped = TEMPLATE.format(title=title, summary=summary, body=txt)
        path.write_text(wrapped)
        print("🔧 Wrapped:", path.name)

if __name__ == "__main__":
    main()