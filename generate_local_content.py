#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cannabis Delivery SEO Blog Generator
- Focused ONLY on Etobicoke & Guelph
- Delivery-first content (same-day, legal, ID-checked)
- No products, no affiliates, no accessories
- SEO-optimized for surrounding neighbourhoods
- Safe for automated publishing
"""

import os
import re
import json
import random
import datetime
from pathlib import Path
from typing import List, Dict

# -----------------------------
# Core config
# -----------------------------
POSTS_DIR      = Path("posts")
LOG_FILE       = Path(".article_log.json")
NEW_POST_COUNT = int(os.environ.get("NEW_POST_COUNT", "4"))

# HARD LOCKED LOCATIONS
STORE_LOCATIONS = ["Etobicoke", "Guelph"]

# Neighbourhood SEO expansion (used naturally in body text)
SURROUNDING_AREAS = {
    "Etobicoke": [
        "Rexdale", "Mimico", "Islington",
        "Alderwood", "The Queensway"
    ],
    "Guelph": [
        "Downtown Guelph", "South End",
        "West End", "Exhibition Park"
    ]
}

# -----------------------------
# DELIVERY-FIRST TOPICS ONLY
# -----------------------------
BASE_TOPICS = [
    "Cannabis Delivery in {city}: Same-Day Legal Weed Delivery",
    "Same-Day Cannabis Delivery in {city}: How It Works",
    "Is Cannabis Delivery Legal in {city}?",
    "How Cannabis Delivery Works in {city}",
    "Fast & Reliable Cannabis Delivery in {city}",
]

# -----------------------------
# Utilities
# -----------------------------
SLUG_PAT = re.compile(r"[^a-z0-9-]+")

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[’'“”]", "", text)
    text = re.sub(r"\s+", "-", text)
    return SLUG_PAT.sub("-", text).strip("-")

def load_log() -> Dict:
    if not LOG_FILE.exists():
        return {"titles": []}
    try:
        data = json.loads(LOG_FILE.read_text(encoding="utf-8"))
        if isinstance(data, dict) and "titles" in data:
            return data
        if isinstance(data, list):
            return {"titles": data}
    except Exception:
        pass
    return {"titles": []}

def save_log(log: Dict):
    LOG_FILE.write_text(json.dumps(log, indent=2), encoding="utf-8")

# -----------------------------
# Content generators
# -----------------------------
def seo_intro(city: str) -> str:
    areas = ", ".join(SURROUNDING_AREAS[city][:3])
    return (
        f"<p><strong>Cannabis delivery in {city}</strong> is a fast, legal, and convenient way "
        f"to receive cannabis products at home. Reserved Cannabis offers same-day cannabis "
        f"delivery across {city}, including nearby areas like {areas}. "
        "All deliveries follow Ontario regulations and require valid ID at the door.</p>"
    )

def delivery_sections(city: str) -> str:
    return f"""
<h2>Same-Day Cannabis Delivery in {city}</h2>
<p>Most orders placed earlier in the day qualify for same-day cannabis delivery in {city}.
Delivery windows are selected at checkout and confirmed before dispatch.</p>

<h2>How Cannabis Delivery Works</h2>
<p>Order online, choose a delivery window, and receive confirmation by email or SMS.
Your driver will verify government-issued ID upon arrival.</p>

<h2>Legal & Safe Cannabis Delivery</h2>
<p>Cannabis delivery in {city} is legal for adults 19+ under Ontario law.
All deliveries are handled discreetly and in compliance with AGCO regulations.</p>
"""

def local_area_section(city: str) -> str:
    areas = SURROUNDING_AREAS[city]
    area_list = ", ".join(areas)
    return (
        f"<h2>Areas We Serve Around {city}</h2>"
        f"<p>In addition to central {city}, we regularly deliver to nearby neighbourhoods such as "
        f"{area_list}. Availability may vary slightly by route and demand.</p>"
    )

def render_article(title: str, city: str) -> str:
    today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <meta name="description" content="Learn how cannabis delivery in {city} works. Same-day, legal weed delivery with ID verification. Serving surrounding neighbourhoods.">
</head>
<body>
<article>
<h1>{title}</h1>
<time datetime="{today}">{today}</time>
{seo_intro(city)}
{delivery_sections(city)}
{local_area_section(city)}
</article>
</body>
</html>
"""

# -----------------------------
# Main
# -----------------------------
def main():
    POSTS_DIR.mkdir(exist_ok=True)
    log = load_log()
    seen = set(log.get("titles", []))

    created = 0
    new_titles = []

    for city in STORE_LOCATIONS:
        for topic_tpl in BASE_TOPICS:
            if created >= NEW_POST_COUNT:
                break

            title = topic_tpl.format(city=city)
            if title in seen:
                continue

            slug = slugify(title)
            out = POSTS_DIR / f"{slug}.html"
            if out.exists():
                continue

            html = render_article(title, city)
            out.write_text(html, encoding="utf-8")

            seen.add(title)
            new_titles.append(title)
            created += 1

    if new_titles:
        save_log({"titles": sorted(seen)})
        print(f"✅ Published {len(new_titles)} new delivery-focused blog posts.")
    else:
        print("ℹ️ No new posts generated.")

if __name__ == "__main__":
    main()