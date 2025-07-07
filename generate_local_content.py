import os
import openai
from config import OPENAI_API_KEY
from datetime import datetime

openai.api_key = OPENAI_API_KEY

topics = [
    "Best strains for relaxation in Ontario",
    "Understanding hybrid cannabis effects",
    "Cannabis and sleep – what studies say",
    "Cannabis laws in Ontario 2025 update",
    "Tips for first-time cannabis users",
]

def sanitize_filename(name):
    return name.lower().replace(" ", "_").replace("-", "_").replace("–", "_").replace("'", "").replace(",", "") + ".html"

for topic in topics:
    try:
        prompt = f"Write a 500-word SEO-optimized blog article on the topic: '{topic}'. Include a strong headline but no title tags. Format using <p> and <h2> tags only. Avoid H1."
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        content = response.choices[0].message.content.strip()
        filename = sanitize_filename(topic)
        with open(f"posts/{filename}", "w") as f:
            f.write(content)
        print(f"✅ Saved: {filename}")
    except Exception as e:
        print(f"❌ Error with topic '{topic}':", e)