import os

TERMS = [
    "dispensary near me",
    "cannabis store",
    "cannabis",
    "dispensary",
    "reserved cannabis"
]

def create_articles():
    os.makedirs("posts/generated", exist_ok=True)
    for term in TERMS:
        slug = term.replace(" ", "-")
        with open(f"posts/generated/{slug}.html", "w") as f:
            f.write(f"""
<!DOCTYPE html><html><head><title>{term.title()}</title></head>
<body>
  <h1>{term.title()}</h1>
  <p>If you're searching for <strong>{term}</strong>, Reserved Cannabis Waterloo is the place to go.</p>
</body></html>
""")

if __name__ == '__main__':
    create_articles()

