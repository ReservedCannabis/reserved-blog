#!/usr/bin/env python3
import os, glob, re, datetime
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, ElementTree

# change this if your feed is hosted elsewhere
BASE_URL = "https://blog.reservedcannabis.ca"  
POSTS_DIR = "posts"

def get_featured_image(post_path):
    """Find the first <img src="..."> in the generated HTML."""
    html = open(post_path, encoding="utf-8").read()
    m = re.search(r'<img\s+src="([^"]+)"', html)
    if not m:
        return None
    src = m.group(1)
    # make absolute
    if src.startswith("http"):
        return src
    if src.startswith("/"):
        return BASE_URL + src
    return BASE_URL + "/" + src

def main():
    # root <rss> and <channel>
    rss = Element("rss", version="2.0")
    ch  = SubElement(rss, "channel")
    SubElement(ch, "title").text       = "Reserved Cannabis Blog"
    SubElement(ch, "link").text        = BASE_URL
    SubElement(ch, "description").text = "Latest articles from Reserved Cannabis"

    # pick 10 newest posts
    all_posts = sorted(glob.glob(f"{POSTS_DIR}/*.html"),
                       key=os.path.getmtime, reverse=True)[:10]

    for path in all_posts:
        filename = os.path.basename(path)
        slug     = filename
        url      = f"{BASE_URL}/{POSTS_DIR}/{slug}"

        item = SubElement(ch, "item")
        SubElement(item, "title").text   = filename.rsplit(".",1)[0].replace("_"," ").replace("-"," ").title()
        SubElement(item, "link").text    = url
        mtime = os.path.getmtime(path)
        pub   = datetime.datetime.utcfromtimestamp(mtime)\
                  .strftime("%a, %d %b %Y %H:%M:%S +0000")
        SubElement(item, "pubDate").text = pub

        # add enclosure if we found an image
        img = get_featured_image(path)
        if img:
            enc = SubElement(item, "enclosure")
            enc.set("url", img)
            # optional: set MIME type
            ext = img.lower().rsplit(".",1)[-1]
            enc.set("type", f"image/{'png' if ext=='png' else 'jpeg'}")

    # write out rss.xml
    tree = ElementTree(rss)
    tree.write("rss.xml", encoding="utf-8", xml_declaration=True)
    print("✅ rss.xml generated")

if __name__ == "__main__":
    main()