"""Calendar management agent."""
import logging
from datetime import datetime
from typing import Any, Dict, List

from agents.base_agent import BaseAgent
from ingestion.calendar_sync import CalendarSync

logger = logging.getLogger(__name__)


class CalendarAgent(BaseAgent):
    """Agent for calendar operations and scheduling."""

    def __init__(self):
        """Initialize calendar agent."""
        super().__init__("CalendarAgent")
        self.calendar_sync = CalendarSync()

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process calendar-related request.

        Args:
            input_data: Request data with 'action' key

        Returns:
            Processing results
        """
        action = input_data.get("action")

        if action == "sync_events":
            return await self.sync_events(input_data.get("days_ahead", 7))
        elif action == "find_free_time":
            return await self.find_free_time(input_data)
        elif action == "suggest_meeting_times":
            return await self.suggest_meeting_times(input_data)
        else:
            return {"success": False, "error": f"Unknown action: {action}"}

    async def sync_events(self, days_ahead: int = 7) -> Dict[str, Any]:
        """
        Sync calendar events from Google Calendar.

        Args:
            days_ahead: Number of days to sync

        Returns:
            Sync results
        """
        try:
            events = self.calendar_sync.get_upcoming_events(days_ahead)

            self.log_action(
                "sync_calendar_events",
                input_data={"days_ahead": days_ahead},
                output_data={"event_count": len(events)},
                success=True,
            )

            return {
                "success": True,
                "event_count": len(events),
                "events": events,
            }

        except Exception as e:
            logger.error(f"Error syncing calendar events: {e}")
            self.log_action(
                "sync_calendar_events",
                input_data={"days_ahead": days_ahead},
                success=False,
                error=str(e),
            )
            return {"success": False, "error": str(e)}

    async def find_free_time(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Find free time slots in calendar.

        Args:
            params: Parameters including date, duration, etc.

        Returns:
            Available time slots
        """
        try:
            date = params.get("date")
            duration = params.get("duration", 60)  # minutes

            # Sync calendar for the target date
            events = self.calendar_sync.get_upcoming_events(days_ahead=7)

            # Use AI to find optimal free slots
            system_prompt = """You are a scheduling assistant. Analyze the calendar
            events and identify free time slots that would be suitable for the
            requested duration. Consider work hours (9 AM - 5 PM) and avoid back-to-back
            meetings when possible."""

            event_summary = "\n".join(
                [
                    f"- {e['summary']}: {e['start_time']} to {e['end_time']}"
                    for e in events
                ]
            )

            prompt = f"""Calendar events:\n{event_summary}\n\n
            Find free {duration}-minute slots on {date or 'today'}.
            Suggest 3-5 optimal time slots."""

            response = await self.call_llm(prompt, system_prompt, max_tokens=1024)

            return {
                "success": True,
                "date": date,
                "duration": duration,
                "suggestions": response,
            }

        except Exception as e:
            logger.error(f"Error finding free time: {e}")
            return {"success": False, "error": str(e)}

    async def suggest_meeting_times(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Suggest optimal meeting times based on calendar and preferences.

        Args:
            params: Meeting requirements

        Returns:
            Suggested meeting times
        """
        try:
            duration = params.get("duration", 30)
            participants = params.get("participants", [])
            date_range = params.get("date_range", 7)

            events = self.calendar_sync.get_upcoming_events(days_ahead=date_range)

            system_prompt = """You are a meeting scheduling assistant. Suggest
            optimal meeting times that:
            1. Avoid conflicts with existing events
            2. Prefer mornings for important meetings
            3. Leave buffer time between meetings
            4. Consider typical lunch hours (12-1 PM)"""

            event_summary = "\n".join(
                [f"- {e['summary']}: {e['start_time']} to {e['end_time']}" for e in events]
            )

            prompt = f"""Existing events:\n{event_summary}\n\n
            Suggest 5 optimal times for a {duration}-minute meeting
            over the next {date_range} days."""

            response = await self.call_llm(prompt, system_prompt, max_tokens=1024)

            return {
                "success": True,
                "duration": duration,
                "suggestions": response,
            }

        except Exception as e:
            logger.error(f"Error suggesting meeting times: {e}")
            return {"success": False, "error": str(e)}
