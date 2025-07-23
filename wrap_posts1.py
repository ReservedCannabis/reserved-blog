#!/usr/bin/env python3
import os

WRAPPER = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body {{
      background: #000;
      color: #fff;
      font-family: Arial, sans-serif;
      line-height: 1.6;
      padding: 20px;
      max-width: 800px;
      margin: auto;
    }}
    img {{ max-width: 100%; height: auto; border-radius: 12px; margin-bottom: 20px; }}
    a {{ color: #4fc3f7; text-decoration: underline; }}
    h1, h2, h3 {{ color: #ffd54f; }}
    p {{ margin-bottom: 1em; }}
  </style>
</head>
<body>
{body}
</body>
</html>"""

for fname in sorted(os.listdir("posts")):
    if not fname.endswith(".html"):
        continue

    path = os.path.join("posts", fname)
    raw = open(path).read()

    # pull out any existing <body>…</body>
    # assume raw is just the inner snippet
    title = os.path.splitext(fname)[0].replace("_", " ").title()
    wrapped = WRAPPER.format(title=title, body=raw)

    with open(path, "w") as f:
        f.write(wrapped)

    print(f"🔧 Wrapped: posts/{fname}")
