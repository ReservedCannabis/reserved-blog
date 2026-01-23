import os
from glob import glob

SCHEMA = '''<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "Reserved Cannabis",
  "image": "https://reservedcannabis.ca/logo.png",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "646 Erb St. W #101",
    "addressLocality": "Waterloo",
    "addressRegion": "ON",
    "postalCode": "N2T 0A8",
    "addressCountry": "CA"
  },
  "telephone": "+15192085999"
}
</script>'''

def add_schema():
    for fpath in glob("posts/**/*.html", recursive=True):
        with open(fpath, 'r+') as f:
            html = f.read()
            if "LocalBusiness" not in html:
                html = html.replace("</head>", f"{SCHEMA}</head>")
                f.seek(0)
                f.write(html)
                f.truncate()

if __name__ == '__main__':
    add_schema()

