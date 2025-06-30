
# Simulated keyword tracker – real version would require GSC API setup
import datetime
from google_sheets_logger import log_to_sheet

keywords = {
    "etobicoke weed delivery": 14,
    "waterloo cannabis store": 22,
    "same day cannabis delivery ontario": 35
}

for kw, pos in keywords.items():
    log_to_sheet("track_keywords", kw, f"Current rank: {pos}", datetime.datetime.now().isoformat())
