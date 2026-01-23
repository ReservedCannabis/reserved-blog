import os
from glob import glob

REVIEW_WIDGET = '''<div style="text-align:center;margin-top:20px;">
  ⭐ 4.8/5 on Google – <a href="https://www.google.com/search?q=reserved+cannabis+waterloo&hl=en" target="_blank">Read 180+ reviews</a>
</div>'''

def insert_reviews():
    for file in glob("posts/**/*.html", recursive=True):
        with open(file, 'r+') as f:
            html = f.read()
            if "4.8/5 on Google" not in html:
                html = html.replace("</body>", f"{REVIEW_WIDGET}</body>")
                f.seek(0)
                f.write(html)
                f.truncate()

if __name__ == '__main__':
    insert_reviews()

