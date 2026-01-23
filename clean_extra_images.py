#!/usr/bin/env python3
import os
from bs4 import BeautifulSoup

DIRS = ["posts", "posts_wrapped"]

def before_first_heading(el, boundary):
    cur = el
    while cur and cur is not boundary:
        sib = cur.find_previous_sibling()
        if sib and getattr(sib, "name", "").lower().startswith("h"):
            return False
        cur = cur.parent
    return True

def clean_one(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    content = soup.find("section", {"class":"rc-content"}) or soup.body
    if not content:
        return False

    # Keep ONE featured (if present) + ONE in-body image after the first heading/paragraph
    featured = content.find("figure", id="featured-image")
    keep_src = None
    if featured:
        img = featured.find("img")
        keep_src = img.get("src") if img else None

    removed = 0

    # 1) Drop any images/figures BEFORE the first heading (except featured block)
    for el in list(content.find_all(["img","figure"])):
        if featured and el is featured:
            continue
        if before_first_heading(el, content):
            el.decompose()
            removed += 1

    # 2) After first heading: keep only the first non-feature image, remove the rest
    seen_body_img = False
    for el in list(content.find_all(["img","figure"])):
        if featured and el is featured:
            continue
        # resolve to <img>
        im = el if el.name == "img" else el.find("img")
        if not im:
            continue
        if keep_src and im.get("src") == keep_src:
            # duplicate of featured → remove
            el.decompose()
            removed += 1
            continue
        if not seen_body_img:
            seen_body_img = True
            continue
        el.decompose()
        removed += 1

    if removed:
        with open(path, "w", encoding="utf-8") as f:
            f.write(str(soup))
    return removed > 0

def main():
    total=0
    for d in DIRS:
        if not os.path.isdir(d): 
            continue
        for name in os.listdir(d):
            if not name.endswith(".html"): 
                continue
            p = os.path.join(d, name)
            if clean_one(p):
                total += 1
                print(f"🧹 Cleaned: {p}")
    print(f"✅ Done. {total} file(s) cleaned.")

if __name__ == "__main__":
    main()
