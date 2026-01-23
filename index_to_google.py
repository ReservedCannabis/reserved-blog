#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Google Indexing API — SAFE MODE
- Submits ONLY newly created Etobicoke/Guelph delivery pages
- Avoids legacy junk and invalid URLs
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from google.oauth2 import service_account
from googleapiclient.discovery import build

CREDENTIALS_FILE = "google-credentials.json"
LOG_FILE = Path(".article_log.json")
POSTS_DIR = Path("posts")

BASE_URL = "https://reservedcannabis.github.io/reserved-blog/posts/"
SCOPES = ["https://www.googleapis.com/auth/indexing"]

ALLOWED_CITIES = ("etobicoke", "guelph")

def slugify(title: str) -> str:
    t = title.lower()
    for c in ["’", "'", "“", "”", ":", "&", "?", ","]:
        t = t.replace(c, "")
    return "-".join(t.split())

def get_recent_post_urls(hours=2):
    cutoff = datetime.now(timezone.utc).timestamp() - (hours * 3600)
    urls = []

    for f in POSTS_DIR.glob("*.html"):
        if f.stat().st_mtime < cutoff:
            continue

        slug = f.stem.lower()
        if not any(city in slug for city in ALLOWED_CITIES):
            continue

        urls.append(f"{BASE_URL}{f.name}")

    return urls

def main():
    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=SCOPES
    )
    service = build("indexing", "v3", credentials=creds)

    urls = get_recent_post_urls()
    if not urls:
        print("ℹ️ No new delivery URLs to submit.")
        return

    submitted = 0
    for url in urls:
        try:
            service.urlNotifications().publish(
                body={"url": url, "type": "URL_UPDATED"}
            ).execute()
            print(f"✅ Indexed: {url}")
            submitted += 1
        except Exception as e:
            print(f"⚠️ Failed: {url} — {e}")

    print(f"\n🚀 Google Indexing API: submitted {submitted} URL(s)")

if __name__ == "__main__":
    main()