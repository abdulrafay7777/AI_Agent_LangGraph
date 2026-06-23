"""Google Calendar integration node using OAuth2 for the LangGraph agent."""

from __future__ import annotations

import os
from typing import Dict, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

def _get_calendar_service():
    """Create an authorized Google Calendar service object using OAuth2."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists("credentials.json"):
                raise FileNotFoundError(
                    "Missing 'credentials.json'. Please download your OAuth 2.0 Client ID "
                    "from the Google Cloud Console and save it as 'credentials.json' in the root directory."
                )
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            # This will open a browser window for authentication
            # Using port 8080 to allow users to whitelist it if using a Web client
            creds = flow.run_local_server(port=8080)
            
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)


def add_event(
    *,
    summary: str,
    start_iso: str,
    end_iso: str,
    location: Optional[str] = None,
    description: Optional[str] = None,
) -> Dict:
    """
    Create a new event in the primary Google Calendar.

    Args:
        summary: Title of the event.
        start_iso: ISO 8601 formatted start datetime (e.g. "2026-06-25T14:00:00Z").
        end_iso: ISO 8601 formatted end datetime.
        location: Optional location string.
        description: Optional description/notes for the event.

    Returns:
        The inserted event resource as a dict.

    Raises:
        RuntimeError: If the calendar API call fails.
    """
    try:
        service = _get_calendar_service()
        event_body = {
            "summary": summary,
            "start": {"dateTime": start_iso, "timeZone": "UTC"},
            "end": {"dateTime": end_iso, "timeZone": "UTC"},
        }
        if location:
            event_body["location"] = location
        if description:
            event_body["description"] = description

        created_event = (
            service.events()
            .insert(calendarId="primary", body=event_body)
            .execute()
        )
        return created_event
    except Exception as exc:
        raise RuntimeError(f"Failed to add calendar event: {exc}") from exc