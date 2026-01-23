import os, glob, datetime
from bs4 import BeautifulSoup

# Prefer wrapped posts for consistent styling; fall back to raw posts if needed
SEARCH_DIRS = ["posts_wrapped", "posts"]
FEED_FILE   = "blog-feed.html"
MAX_CARDS   = 120  # show more so new items surface

STYLE = """
<style>
  body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Oxygen,Ubuntu,Cantarell,"Open Sans","Helvetica Neue",sans-serif;margin:0;padding:0;background:#efe9e4}
  h1{padding:2rem;margin:0;font-size:2rem}
  .container{padding:2rem;display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:1.25rem}
  .card{background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 14px rgba(0,0,0,.08);display:flex;flex-direction:column;transition:transform .18s ease}
  .card:hover{transform:translateY(-4px)}
  .card img{width:100%;height:180px;object-fit:cover}
  .card-content{padding:1rem}
  .card-content h2{font-size:1.05rem;margin:0 0 .35rem}
  .card-content p{color:#666;font-size:.85rem;margin:0}
  a{text-decoration:none;color:inherit}
</style>
"""

def parse_date_from_soup(soup):
    # Prefer <time datetime="YYYY-MM-DD">, then text of <time>, then None
    t = soup.find("time")
    if t:
        if t.has_attr("datetime"):
            try:
                return datetime.datetime.strptime(t["datetime"][:10], "%Y-%m-%d")
            except Exception:
                pass
        if t.text and t.text.strip():
            for fmt in ("%Y-%m-%d", "%b %d, %Y", "%Y/%m/%d"):
                try:
                    return datetime.datetime.strptime(t.text.strip()[:12], fmt)
                except Exception:
                    continue
    return None

def post_iter():
    seen = set()
    for d in SEARCH_DIRS:
        if not os.path.isdir(d): 
            continue
        for fp in glob.glob(os.path.join(d, "*.html")):
            slug = os.path.basename(fp)
            if slug in seen:
                continue
            seen.add(slug)
            yield d, fp, slug

def card_info(dir_name, path, slug):
    with open(path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    title = (soup.title.text.strip() if soup.title and soup.title.text.strip() else slug.replace("-", " ").title())
    dt = parse_date_from_soup(soup)
    # Fallback: if no <time>, use the *source* post mtime rather than wrapped mtime
    if dt is None:
        source_path = path
        if dir_name == "posts_wrapped":
            raw = os.path.join("posts", slug)
            if os.path.exists(raw):
                source_path = raw
        ts = os.path.getmtime(source_path)
        dt = datetime.datetime.utcfromtimestamp(ts)
    # Card image: first <img> src if present
    img = ""
    img_tag = soup.find("img")
    if img_tag and img_tag.get("src"):
        img = img_tag["src"]
    href = f"posts_wrapped/{slug}" if os.path.exists(os.path.join("posts_wrapped", slug)) else f"posts/{slug}"
    return {"title": title, "date": dt, "img": img, "href": href, "slug": slug}

def generate():
    posts = [card_info(d, p, s) for d, p, s in post_iter()]
    # Sort newest first, then by slug for stability
    posts.sort(key=lambda x: (x["date"], x["slug"]), reverse=True)
    cards = []
    for post in posts[:MAX_CARDS]:
        img_html = f'<img src="{post["img"]}" alt="{post["title"]}">' if post["img"] else ""
        cards.append(f"""
        <a href="{post['href']}" target="_blank" rel="noopener">
          <div class="card">
            {img_html}
            <div class="card-content">
              <h2>{post['title']}</h2>
              <p>{post['date'].strftime('%b %d, %Y')}</p>
            </div>
          </div>
        </a>""")
    html = f"""<!doctype html><meta charset="utf-8"><title>Reserved Cannabis — Blog</title>
    {STYLE}
    <h1>Reserved Cannabis — Latest Articles</h1>
    <div class="container">{''.join(cards)}</div>"""
    with open(FEED_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ Blog feed generated: {FEED_FILE} with {min(len(posts), MAX_CARDS)} post(s)")

if __name__ == "__main__":
    generate()
