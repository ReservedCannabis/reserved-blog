#!/usr/bin/env python3
import os
import random
from datetime import datetime

def slugify(text):
    return text.lower().replace(' ', '_').replace('–','').replace(':','').replace("'", '')


def main():
    posts_dir = 'posts'
    os.makedirs(posts_dir, exist_ok=True)

    topics = [
        "Best strains for relaxation in Ontario",
        "Understanding hybrid cannabis effects",
        "Cannabis and sleep – what studies say",
        "Cannabis laws in Ontario: 2025 update",
        "Tips for first-time cannabis users",
    ]

    # Shuffle the order so titles vary each run
    random.shuffle(topics)

    for topic in topics:
        slug = slugify(topic)
        filename = f"{slug}.html"
        html = f"""
<!DOCTYPE html>
<html lang=\"en\">  
<head><meta charset=\"UTF-8\"></head>  
<body style=\"background:#000;color:#fff;\">  
  <h1>{topic}</h1>  
  <p>... your article content ...</p>  
</body>
</html>"""
        path = os.path.join(posts_dir, filename)
        with open(path, 'w') as f:
            f.write(html)
        print(f"✅ Saved: {filename}")

if __name__ == '__main__':
    main()