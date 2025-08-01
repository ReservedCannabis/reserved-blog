import os
import requests
import random

PEXELS_API_KEY = "p8oZVpjpvQJAApFmltlSjdmqWRjIna6j0G62aVja5oKFJchMuusEu3e5"
headers = { "Authorization": PEXELS_API_KEY }

response = requests.get("https://api.pexels.com/v1/search?query=cannabis&per_page=50", headers=headers).json()
photos = response.get("photos", [])
if not photos:
    print("❌ No images fetched from Pexels.")
    exit()

image_urls = [p["src"]["large"] for p in photos]
random.shuffle(image_urls)

for idx, file in enumerate(sorted(os.listdir("posts"))):
    if not file.endswith(".html"): continue
    filepath = os.path.join("posts", file)
    with open(filepath, "r") as f:
        html = f.read()

    img_tag = f'<img src="{image_urls[idx % len(image_urls)]}" style="max-width:100%;height:auto;border-radius:12px;margin-bottom:20px;" alt="Cannabis image">'
    
    if "<style>" not in html:
        html = html.replace("<body>", """<body>
<style>body{color:#fff;font-size:1.2em;line-height:1.6;}</style>""")
    
    with open(filepath, "w") as f:
        f.write(img_tag + html)
    print(f"✅ Added image to {file}")