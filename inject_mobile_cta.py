import os
from glob import glob

CTA_HTML = '''
<div id="mobile-cta-bar" style="position:fixed;bottom:0;width:100%;background:#111;color:#fff;text-align:center;padding:10px;font-size:18px;z-index:9999;">
  📍 <a href="https://goo.gl/maps/YOURMAP" style="color:#0f0;">Find Us</a> |
  📞 <a href="tel:+15192085999" style="color:#0f0;">Call</a> |
  🛒 <a href="https://www.reservedcannabis.ca/shop" style="color:#0f0;">Shop</a>
</div>
'''

def inject_cta():
    for filepath in glob("posts/**/*.html", recursive=True):
        with open(filepath, 'r+') as f:
            content = f.read()
            if "mobile-cta-bar" not in content:
                content = content.replace("</body>", f"{CTA_HTML}</body>")
                f.seek(0)
                f.write(content)
                f.truncate()

if __name__ == '__main__':
    inject_cta()

