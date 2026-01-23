#!/usr/bin/env python3
from pathlib import Path
import requests, uuid, random, time

POST_DIR = Path("posts")
IMG_DIR = Path("assets/images")
IMG_DIR.mkdir(parents=True, exist_ok=True)

KEYWORDS = [
    "cannabis flower",
    "cannabis buds",
    "cannabis accessories",
    "dispensary interior",
    "cannabis lifestyle"
]

FALLBACK_IMAGE = "https://images.unsplash.com/photo-1603909223429-69bb7101f420?w=1600&auto=format&fit=crop"

def fetch_image():
    query = random.choice(KEYWORDS).replace(" ", ",")
    url = f"https://source.unsplash.com/1600x900/?{query}"

    for attempt in range(3):
        try:
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                return r.content
        except Exception:
            pass

        print(f"⚠️ Unsplash retry {attempt + 1}/3")
        time.sleep(2)

    # Fallback (guaranteed)
    print("⚠️ Using fallback image")
    r = requests.get(FALLBACK_IMAGE, timeout=15)
    r.raise_for_status()
    return r.content

def main():
    for post in POST_DIR.glob("*.html"):
        html = post.read_text(encoding="utf-8")

        if "<img" in html:
            continue  # already has image

        img_bytes = fetch_image()
        img_name = f"{uuid.uuid4().hex}.jpg"
        img_path = IMG_DIR / img_name
        img_path.write_bytes(img_bytes)

        hero = (
            f'<img src="/assets/images/{img_name}" '
            f'alt="Cannabis education article" class="hero">\n'
        )

        post.write_text(hero + html, encoding="utf-8")
        print(f"✅ Added hero image → {post.name}")

if __name__ == "__main__":
    main()