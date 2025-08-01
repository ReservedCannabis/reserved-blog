#!/usr/bin/env python3
import os
import json
import datetime
import random
import openai
from pathlib import Path
from slugify import slugify

# ── CONFIG ────────────────────────────────────────────────────────────────
MODEL        = "gpt-4o-mini"         # change if you like
NEW_TOPICS   = [
    "Best strains for relaxation in Ontario",
    "Understanding hybrid cannabis effects",
    "Cannabis and sleep – what studies say",
    "Cannabis laws in Ontario: 2025 update",
    "Tips for first-time cannabis users",
    "Pre-roll accessories every beginner needs",
    "Maintaining optimal cannabis humidity",
    "Storing cannabis safely at home",
    "Top cannabis grinders compared",
    "How to choose the right THC vs CBD ratio",
]
NUM_NEW      = 5                     # how many new articles per run
TOKENS       = 1500

# ── SETUP ────────────────────────────────────────────────────────────────
openai.api_key = os.getenv("OPENAI_API_KEY")
OUTDIR   = Path("posts")
LOG_FILE = Path(".article_log.json")
OUTDIR.mkdir(exist_ok=True)

# ── HELPERS ───────────────────────────────────────────────────────────────
def load_log():
    if LOG_FILE.exists():
        return set(json.loads(LOG_FILE.read_text()))
    return set()

def save_log(log):
    LOG_FILE.write_text(json.dumps(sorted(log), indent=2))

def brainstorm_topics(candidates, already):
    prompt = (
        "You are a cannabis blog content planner.  From this list:\n\n"
        + "\n".join(f"- {t}" for t in candidates)
        + "\n\nReturn exactly "
        + str(NUM_NEW)
        + " titles that have NOT been used before (each on its own line)."
    )
    resp = openai.ChatCompletion.create(
        model=MODEL,
        messages=[{"role":"user","content":prompt}],
        temperature=0.8,
    )
    lines = resp.choices[0].message.content.strip().splitlines()
    picked = []
    for line in lines:
        title = line.strip(" -1234567890. ")
        if title and title not in already:
            picked.append(title)
        if len(picked) == NUM_NEW:
            break
    return picked

def generate_article(title):
    system  = "You are a friendly, informative cannabis blogger."
    user    = (
        f"Write a ~500-word HTML snippet article on “{title}.” "
        "Include a one-sentence intro, 3 subheadings with 1–2 paragraphs each, "
        "and a one-sentence conclusion. Wrap all in <article>…</article>."
    )
    resp = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {"role":"system", "content":system},
            {"role":"user",   "content":user}
        ],
        temperature=0.7,
        max_tokens=TOKENS
    )
    return resp.choices[0].message.content

def make_page(title, body_html):
    slug = slugify(title)
    pub  = datetime.datetime.now().strftime("%Y-%m-%d")
    full = f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8">
  <title>{title}</title>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <style>body{{background:#000;color:#fff;padding:1rem;font-family:sans-serif}}</style>
</head>
<body>
  <h1>{title}</h1>
  <p><em>Published {pub}</em></p>
  {body_html}
</body>
</html>
"""
    path = OUTDIR / f"{slug}.html"
    path.write_text(full, encoding="utf-8")
    return slug

# ── MAIN ─────────────────────────────────────────────────────────────────
def main():
    used     = load_log()
    candidates = NEW_TOPICS.copy()
    random.shuffle(candidates)
    new_titles = brainstorm_topics(candidates, used)
    if not new_titles:
        print("No fresh topics found – exiting.")
        return

    for t in new_titles:
        print("🔍 Generating article on:", t)
        html = generate_article(t)
        slug = make_page(t, html)
        used.add(t)
        print(f"✅ Saved: posts/{slug}.html")

    save_log(used)
    print(f"📝 .article_log.json now has {len(used)} titles total.")

if __name__ == "__main__":
    main()