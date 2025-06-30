
import os
import datetime
from xml.etree.ElementTree import Element, SubElement, ElementTree

def make_rss(posts_dir="posts", output="rss.xml"):
    rss = Element("rss", version="2.0")
    channel = SubElement(rss, "channel")
    SubElement(channel, "title").text = "Reserved Cannabis Blog"
    SubElement(channel, "link").text = "https://www.reservedcannabis.ca/cannabis-education"
    SubElement(channel, "description").text = "SEO-optimized cannabis blog articles for Ontario consumers"

    for filename in sorted(os.listdir(posts_dir), reverse=True):
        if not filename.endswith(".html"):
            continue
        filepath = os.path.join(posts_dir, filename)
        with open(filepath, "r") as f:
            content = f.read()

        title = filename.replace("-", " ").replace(".html", "").title()
        post_link = f"https://www.reservedcannabis.ca/blog/{filename}"
        item = SubElement(channel, "item")
        SubElement(item, "title").text = title
        SubElement(item, "link").text = post_link
        SubElement(item, "description").text = content[:300] + "..."
        SubElement(item, "pubDate").text = datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")

    ElementTree(rss).write(output, encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    os.makedirs("posts", exist_ok=True)
    make_rss()
