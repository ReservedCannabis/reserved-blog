# rss_generator.py
import os
import datetime
from xml.etree.ElementTree import Element, SubElement, ElementTree

def make_rss(posts_dir="posts", output="rss.xml"):
    rss = Element("rss", version="2.0")
    channel = SubElement(rss, "channel")
    SubElement(channel, "title").text = "Reserved Cannabis Blog"
    SubElement(channel, "link").text = "https://www.reservedcannabis.ca/cannabis-education"
    SubElement(channel, "description").text = "Cannabis blog content for Ontario consumers"

    for filename in sorted(os.listdir(posts_dir), reverse=True):
        if not filename.endswith(".html"):
            continue
        filepath = os.path.join(posts_dir, filename)
        with open(filepath, "r") as f:
            content = f.read()

        title = filename.replace("_", " ").replace(".html", "").title()
        post_link = f"https://reservedcannabis.github.io/reserved-blog/posts/{filename}"
        summary = content[:300].replace("<", "").replace(">", "").strip()

        item = SubElement(channel, "item")
        SubElement(item, "title").text = title
        SubElement(item, "link").text = post_link
        SubElement(item, "description").text = summary + "..."
        SubElement(item, "pubDate").text = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")

    ElementTree(rss).write(output, encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    make_rss()
