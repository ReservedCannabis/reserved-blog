#!/bin/bash

# Change to the SEOAgent folder
cd "$(dirname "$0")"

# Initialize Git only if it hasn't been already
if [ ! -d ".git" ]; then
  git init
  git remote add origin https://github.com/smarthomepulse/reserved-blog.git
  touch .nojekyll
  git add .
  git commit -m "Initial commit"
  git branch -M main
  git push -u origin main
else
  git add rss.xml posts/
  git commit -m "Update RSS feed and posts"
  git push
fi
