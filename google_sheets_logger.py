
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import GOOGLE_CREDENTIALS, SHEET_NAME

def log_to_sheet(task, url, change, timestamp):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDENTIALS, scope)
    client = gspread.authorize(creds)
    sheet = client.open(SHEET_NAME).sheet1
    sheet.append_row([timestamp, task, url, change])
