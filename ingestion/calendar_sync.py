"""Google Calendar synchronization."""
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from config import get_settings

logger = logging.getLogger(__name__)

# Scopes for Google Calendar API
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


class CalendarSync:
    """Sync events from Google Calendar."""

    def __init__(self):
        """Initialize calendar sync."""
        self.settings = get_settings()
        self.service = None

    def authenticate(self) -> bool:
        """
        Authenticate with Google Calendar API.

        Returns:
            True if authentication successful, False otherwise
        """
        creds = None

        # Load existing credentials
        token_file = Path(self.settings.google_token_file)
        if token_file.exists():
            creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)

        # If no valid credentials, let user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not self.settings.google_credentials_file:
                    logger.error("Google credentials file not configured")
                    return False

                credentials_path = Path(self.settings.google_credentials_file)
                if not credentials_path.exists():
                    logger.error(f"Credentials file not found: {credentials_path}")
                    return False

                flow = InstalledAppFlow.from_client_secrets_file(
                    str(credentials_path), SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save credentials for next run
            with open(token_file, "w") as token:
                token.write(creds.to_json())

        try:
            self.service = build("calendar", "v3", credentials=creds)
            logger.info("Successfully authenticated with Google Calendar")
            return True
        except Exception as e:
            logger.error(f"Error building calendar service: {e}")
            return False

    def get_upcoming_events(self, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """
        Get upcoming calendar events.

        Args:
            days_ahead: Number of days ahead to fetch events

        Returns:
            List of event dictionaries
        """
        if not self.service:
            if not self.authenticate():
                return []

        try:
            now = datetime.utcnow()
            time_max = now + timedelta(days=days_ahead)

            events_result = self.service.events().list(
                calendarId="primary",
                timeMin=now.isoformat() + "Z",
                timeMax=time_max.isoformat() + "Z",
                maxResults=100,
                singleEvents=True,
                orderBy="startTime",
            ).execute()

            events = events_result.get("items", [])
            logger.info(f"Fetched {len(events)} upcoming events")

            return self._format_events(events)

        except Exception as e:
            logger.error(f"Error fetching calendar events: {e}")
            return []

    def get_events_in_range(
        self, start_date: datetime, end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Get events in a specific date range.

        Args:
            start_date: Start of date range
            end_date: End of date range

        Returns:
            List of event dictionaries
        """
        if not self.service:
            if not self.authenticate():
                return []

        try:
            events_result = self.service.events().list(
                calendarId="primary",
                timeMin=start_date.isoformat() + "Z",
                timeMax=end_date.isoformat() + "Z",
                singleEvents=True,
                orderBy="startTime",
            ).execute()

            events = events_result.get("items", [])
            return self._format_events(events)

        except Exception as e:
            logger.error(f"Error fetching calendar events: {e}")
            return []

    def _format_events(self, events: List[Dict]) -> List[Dict[str, Any]]:
        """Format calendar events for storage."""
        formatted = []

        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            end = event["end"].get("dateTime", event["end"].get("date"))

            formatted.append({
                "event_id": event["id"],
                "summary": event.get("summary", "No title"),
                "description": event.get("description", ""),
                "location": event.get("location", ""),
                "start_time": start,
                "end_time": end,
                "all_day": "date" in event["start"],
                "status": event.get("status", "confirmed"),
                "attendees": event.get("attendees", []),
                "metadata": {
                    "htmlLink": event.get("htmlLink", ""),
                    "created": event.get("created", ""),
                    "updated": event.get("updated", ""),
                },
            })

        return formatted


def sync_calendar_events(days_ahead: int = 7) -> List[Dict[str, Any]]:
    """Convenience function to sync calendar events."""
    sync = CalendarSync()
    return sync.get_upcoming_events(days_ahead)
