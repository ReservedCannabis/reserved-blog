# reddit_poster.py
import os
import praw
import random

# Load credentials from environment vars or config
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent="cannabis-blog-poster",
    username=os.getenv("REDDIT_USERNAME"),
    password=os.getenv("REDDIT_PASSWORD")
)

subreddits = [
    "ontariocannabis",
    "TheOCS",
    "weed",
    "Marijuana",
    "canadients",
    "trees"
]

# Optional: avoid reposting same title
posted_log = "reddit_posted.txt"
if os.path.exists(posted_log):
    with open(posted_log) as f:
        already_posted = set(f.read().splitlines())
else:
    already_posted = set()

def post_to_reddit(title, url):
    chosen_sub = random.choice(subreddits)
    if title not in already_posted:
        try:
            reddit.subreddit(chosen_sub).submit(title, url=url)
            print(f"✅ Posted to r/{chosen_sub}: {title}")
            with open(posted_log, "a") as f:
                f.write(title + "\n")
        except Exception as e:
            print(f"❌ Failed on r/{chosen_sub}: {e}")
    else:
        print(f"⚠️ Already posted: {title}")

if __name__ == "__main__":
    for filename in sorted(os.listdir("posts"), reverse=True):
        if filename.endswith(".html"):
            title = filename.replace("_", " ").replace(".html", "").title()
            url = f"https://reservedcannabis.github.io/reserved-blog/posts/{filename}"
            post_to_reddit(title, url)
