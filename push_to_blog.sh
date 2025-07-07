#!/bin/bash

echo "📦 Generating updated RSS feed and blog HTML..."
python3 rss_generator.py

echo "🚀 Committing and pushing to ReservedCannabis GitHub Pages repo..."
git add blog-feed.html rss.xml
git commit -m "Update RSS feed and blog content"
git push
echo "✅ Push complete: https://reservedcannabis.github.io/reserved-blog/blog-feed.html"
