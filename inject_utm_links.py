from glob import glob
import re

UTM = "?utm_source=google&utm_medium=gmb&utm_campaign=waterloo_location"

def append_utm():
    for path in glob("posts/**/*.html", recursive=True):
        with open(path, 'r+') as f:
            html = f.read()
            html = re.sub(r'(https://www\.reservedcannabis\.ca[^"\s]*)', r"\1" + UTM, html)
            f.seek(0)
            f.write(html)
            f.truncate()

if __name__ == '__main__':
    append_utm()

