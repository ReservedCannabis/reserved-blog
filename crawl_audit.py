
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import datetime
from google_sheets_logger import log_to_sheet

SITE = "https://www.reservedcannabis.ca"

def get_internal_links(base_url):
    try:
        html = requests.get(base_url, timeout=10).text
        soup = BeautifulSoup(html, 'html.parser')
        links = set()
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('/'):
                links.add(urljoin(base_url, href))
            elif href.startswith(base_url):
                links.add(href)
        return list(links)
    except Exception as e:
        return []

def audit_links():
    urls = get_internal_links(SITE)
    for url in urls:
        try:
            r = requests.get(url, timeout=10)
            if r.status_code != 200:
                log_to_sheet("crawl_audit", url, f"Broken link (Status {r.status_code})", datetime.datetime.now().isoformat())
        except Exception as e:
            log_to_sheet("crawl_audit", url, f"Error: {str(e)}", datetime.datetime.now().isoformat())

if __name__ == "__main__":
    audit_links()
