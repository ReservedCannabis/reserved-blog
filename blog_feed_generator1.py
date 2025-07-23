import os
import datetime

POSTS_DIR = "posts"
OUTPUT_FILE = "blog-feed.html"

def format_post(title, link, snippet, date_str):
    return f'''
    <div class="post">
      <div class="date">{date_str}</div>
      <a href="{link}">{title}</a>
      <div class="summary">{snippet}</div>
    </div>
    '''

def generate_feed():
    posts = []
    for filename in sorted(os.listdir(POSTS_DIR), reverse=True):
        if not filename.endswith(".html"):
            continue
        path = os.path.join(POSTS_DIR, filename)
        with open(path, "r") as f:
            content = f.read()
        title = filename.replace("_", " ").replace(".html", "").title()
        snippet = content.split("</p>")[0].replace("<h1>", "").replace("</h1>", "").strip()
        link = f"posts/{filename}"
        dt = datetime.datetime.utcfromtimestamp(os.path.getmtime(path)).strftime("%a, %d %b %Y")
        posts.append(format_post(title, link, snippet, dt))

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Reserved Cannabis Blog</title>
  <style>
    body {{ background: #111; color: #fff; font-family: Arial, sans-serif; margin: 40px; }}
    h1 {{ border-bottom: 2px solid #ffc107; padding-bottom: 10px; }}
    .post {{ margin-bottom: 40px; padding-bottom: 20px; border-bottom: 1px solid #444; }}
    .post a {{ color: #ffd54f; font-size: 1.4em; text-decoration: none; }}
    .post a:hover {{ text-decoration: underline; }}
    .summary {{ margin-top: 10px; font-size: 1em; line-height: 1.5em; color: #ddd; }}
    .date {{ font-size: 0.9em; color: #aaa; margin-bottom: 8px; }}
  </style>
</head>
<body>
  <h1>Educational Cannabis Articles</h1>
  {''.join(posts)}
</body>
</html>
"""
    with open(OUTPUT_FILE, "w") as f:
        f.write(html)
    print(f"✅ {OUTPUT_FILE} updated with {len(posts)} posts.")

if __name__ == "__main__":
    generate_feed()