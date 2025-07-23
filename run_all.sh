#!/bin/bash

echo "📦 Generating new blog posts…"
python3 generate_local_content.py

echo "🖼 Adding featured images…"
python3 image_fetcher.py

echo "🔗 Populating affiliate links in sheet…"
python3 populate_affiliate_links.py

echo "🛒 Inserting Amazon affiliate products…"
python3 affiliate_inserter.py

echo "🔧 Wrapping posts in full HTML + forcing white text…"
python3 wrap_posts.py

echo "📰 Generating RSS and blog-feed…"
python3 rss_generator.py
python3 blog_feed_generator.py

echo "🚀 Committing and pushing to GitHub Pages…"
bash push_to_blog.sh

echo "🔗 Fetching new affiliate products…"
python3 fetch_reserved_affiliate_products.py

# now regenerate index.html redirect
cat > index.html <<EOF
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Redirecting…</title>
    <meta http-equiv="refresh" content="0;url=blog-feed.html">
  </head>
  <body>
    <p>Redirecting to <a href="blog-feed.html">blog feed</a>…</p>
  </body>
</html>
EOF

git add index.html
git commit -m "Update index.html redirect"
git push