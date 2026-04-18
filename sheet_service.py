import json
import gspread
from google.oauth2.service_account import Credentials
from config import GOOGLE_SHEET_ID, GOOGLE_SERVICE_ACCOUNT_JSON

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

def get_client():
    info = json.loads(GOOGLE_SERVICE_ACCOUNT_JSON)
    creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    return gspread.authorize(creds)

def get_spreadsheet():
    client = get_client()
    return client.open_by_key(GOOGLE_SHEET_ID)

def append_row(sheet_name: str, values: list):
    sh = get_spreadsheet()
    ws = sh.worksheet(sheet_name)
    ws.append_row(values)
