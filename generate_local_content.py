#!/usr/bin/env python3
import os
import re
import random
import datetime
import openai
from pathlib import Path

# ————— CONFIG —————————————————————————————————————————————
openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL       = "gpt-4o-mini"
TEMPERATURE = 0.7
MAX_TOKENS  = 900

# Edit *this* list to control your seed topics:
KEYWORDS = [
    "Best strains for relaxation in Ontario",
    "Understanding hybrid cannabis effects",
    "Cannabis and sleep – what the studies say",
    "Cannabis laws in Ontario: 2025 update",
    "Tips for first-time cannabis users",
    "How to choose the right THC vs CBD ratio",
    "Storing cannabis safely at home",
    "Pre-roll accessories every beginner needs",
    "Maintaining optimal cannabis humidity",
    "Top cannabis grinders compared",
]

def slugify(text: str) -> str:
    t = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"\s+", "_", t)

def generate_article(topic: str) -> str:
    prompt = f"""
You are a Canadian cannabis expert. Write an SEO-optimized blog post on:
“{topic}”

• Return ONLY HTML.
• First line: a single <h1> with the title (exactly the topic).
• Then 4–6 paragraphs, each wrapped in <p>…</p>.
• DO NOT include <html>, <head>, or <body> tags.
"""
    resp = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a friendly, concise cannabis writer."},
            {"role": "user",   "content": prompt},
        ],
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
    )
    return resp.choices[0].message.content.strip()

def main():
    outdir = Path("posts")
    # clear out old files (avoids duplicates)
    for f in outdir.glob("*.html"):
        f.unlink()
    outdir.mkdir(exist_ok=True)

    topics = KEYWORDS.copy()
    random.shuffle(topics)

    for topic in topics:
        print(f"🔍 Generating article on: {topic}")
        html = generate_article(topic)
        if not html:
            print("⚠️ Skipped (no content).")
            continue

        # embed published date comment at top
        pub = datetime.datetime.utcnow().strftime("%Y-%m-%d")
        html = f"<!-- published:{pub} -->\n{html}"

        # write out
        slug = slugify(topic)
        out  = outdir / f"{slug}.html"
        with open(out, "w") as f:
            f.write(html + "\n")
        print("✅ Saved:", out)

if __name__ == "__main__":
    main()