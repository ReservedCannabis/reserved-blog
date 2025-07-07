#!/bin/bash

echo "📦 Generating new blog posts..."
python3 generate_local_content.py

echo "🖼 Adding featured images..."
python3 image_fetcher.py

echo "🛒 Inserting Amazon affiliate products..."
python3 affiliate_inserter.py

echo "📰 Generating RSS and blog-feed..."
python3 rss_generator.py
python3 blog_feed_generator.py

# Optional: Reddit auto-posting (disabled for now)
# echo "🔗 Posting to Reddit..."
# python3 reddit_poster.py

echo "🚀 Committing and pushing to GitHub Pages..."
bash push_to_blog.sh

git add blog-feed.html rss.xml posts/*.html
git commit -m "Update blog feed and articles"
git push