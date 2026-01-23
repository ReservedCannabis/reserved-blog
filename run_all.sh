#!/bin/bash
set -euo pipefail

# Locked service areas (generator enforces this too)
export STORE_LOCATIONS="Etobicoke,Guelph"

echo "📦 Generating any new blog posts…"
python3 generate_local_content.py

echo "🖼 Adding featured images…"
python3 image_fetcher.py || true

echo "🔧 Wrapping posts into styled HTML (idempotent)…"
python3 wrap_posts.py

echo "📦 Adding schema markup…"
python3 inject_schema.py || true

echo "📰 Generating RSS feed…"
python3 rss_generator.py

echo "📰 Generating blog feed grid…"
python3 blog_feed_generator.py

echo "🏷️ Creating/refreshing root redirect -> blog-feed.html"
cat > index.html <<EOF
<!doctype html><meta charset="utf-8">
<meta http-equiv="refresh" content="0;url=blog-feed.html">
<p>Redirecting to <a href="blog-feed.html">blog feed</a>…</p>
EOF

echo "📦 Staging blog files for GitHub Pages…"
git add blog-feed.html rss.xml index.html posts_wrapped/ || true

echo "🚀 Committing and pushing to GitHub Pages…"
git commit -m "Publish blog + RSS ($(date -u '+%Y-%m-%d %H:%M:%S UTC'))" || true
git push origin main

echo "🚀 Submitting blog URLs to Google Indexing API…"
python3 index_to_google.py || true

echo "✅ Done. View: https://reservedcannabis.github.io/reserved-blog/blog-feed.html"