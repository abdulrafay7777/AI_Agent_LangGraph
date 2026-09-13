import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

def get_calendar_service():
    scope = ['https://www.googleapis.com/auth/calendar.events']
    creds_path = os.getenv('GOOGLE_CAL_SERVICE_ACCOUNT')
    creds = Credentials.from_service_account_file(creds_path, scopes=[scope])
    return build('calendar', 'v3', credentials=creds)