import os
from glob import glob

KEYWORDS = ["dispensary near me", "cannabis store", "cannabis Waterloo", "best cannabis shop"]

def boost_keywords():
    for filepath in glob("posts/**/*.html", recursive=True):
        with open(filepath, 'r+') as f:
            content = f.read()
            if "dispensary near me" not in content:
                content = content.replace("<body>", f"<body>\n<!-- keywords: {', '.join(KEYWORDS)} -->")
                f.seek(0)
                f.write(content)
                f.truncate()

if __name__ == '__main__':
    boost_keywords()
