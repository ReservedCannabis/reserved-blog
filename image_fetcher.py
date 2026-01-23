#!/usr/bin/env python3
import os, random
from bs4 import BeautifulSoup

POSTS_DIR = "posts_wrapped"

# ✅ VALID Unsplash image URLs (no downloads, no 404s)
STOCK = [
    "https://images.unsplash.com/photo-1603398938378-e54eab446dde?auto=format&fit=crop&w=1600&q=80",
    "https://images.unsplash.com/photo-1585238342028-4bbc2b5a4f8b?auto=format&fit=crop&w=1600&q=80",
    "https://images.unsplash.com/photo-1615485925873-3f74e1e7a1b1?auto=format&fit=crop&w=1600&q=80",
    "https://images.unsplash.com/photo-1607082349566-187342175e2f?auto=format&fit=crop&w=1600&q=80",
]

def pick_image():
    return random.choice(STOCK)

def main():
    for name in os.listdir(POSTS_DIR):
        if not name.endswith(".html"):
            continue

        path = os.path.join(POSTS_DIR, name)

        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        img_url = pick_image()

        # ---------- SEO: og:image ----------
        if soup.head:
            og = soup.head.find("meta", property="og:image")
            if og:
                og["content"] = img_url
            else:
                soup.head.append(
                    soup.new_tag("meta", property="og:image", content=img_url)
                )

        # ---------- Visible HERO image ----------
        article = soup.find("article") or soup.body
        if not article:
            continue

        existing = article.find("img", {"data-hero": "true"})
        if not existing:
            img = soup.new_tag("img")
            img["src"] = img_url
            img["alt"] = ""
            img["data-hero"] = "true"

            # Inline styles so your theme CANNOT hide it
            img["style"] = (
                "width:100%;"
                "max-height:420px;"
                "object-fit:cover;"
                "display:block;"
                "margin:0 0 32px 0;"
                "border-radius:12px;"
            )

            article.insert(0, img)

        with open(path, "w", encoding="utf-8") as f:
            f.write(str(soup))

        print(f"✅ Inserted hero image → {name}")

if __name__ == "__main__":
    main()