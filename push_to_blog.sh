#!/usr/bin/env bash
set -euo pipefail

# Always run from the repo root
cd "$(dirname "$0")"

echo "🧹 Ensuring generated files exist…"
mkdir -p posts_wrapped

echo "📰 (Re)building RSS + blog feed…"
python3 rss_generator.py
python3 blog_feed_generator.py

echo "🏷️ Creating/refreshing root redirect -> blog-feed.html"
cat > index.html <<'EOF'
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Redirecting…</title>
  <meta http-equiv="refresh" content="0;url=blog-feed.html">
</head>
<body>
  <p>Redirecting to <a href="blog-feed.html">our blog feed</a>…</p>
</body>
</html>
EOF

echo "📦 Staging all generated content…"
git add blog-feed.html rss.xml index.html
git add -A posts_wrapped/ || true            # add new/changed/deleted pages
# If you also keep a posts_with_affiliates dir, uncomment:
# git add -A posts_with_affiliates/ || true

# Skip commit if nothing changed
if git diff --cached --quiet; then
  echo "✅ Nothing new to publish."
  exit 0
fi

# Safer author defaults if not set
git -c user.name="${GIT_COMMITTER_NAME:-Auto Publisher}" \
    -c user.email="${GIT_COMMITTER_EMAIL:-auto@publisher.local}" \
    commit -m "Publish blog + RSS ($(date -u +'%Y-%m-%d %H:%M:%S UTC'))"

echo "🚀 Pushing…"
git push origin main

echo "✅ Live: https://reservedcannabis.github.io/reserved-blog/blog-feed.html"

