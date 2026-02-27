"""Planning and scheduling agent."""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List

from agents.base_agent import BaseAgent
from agents.calendar_agent import CalendarAgent
from agents.task_manager import TaskManagerAgent

logger = logging.getLogger(__name__)


class PlannerAgent(BaseAgent):
    """Agent for high-level planning and scheduling."""

    def __init__(self):
        """Initialize planner agent."""
        super().__init__("PlannerAgent")
        self.calendar_agent = CalendarAgent()
        self.task_manager = TaskManagerAgent()

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process planning request.

        Args:
            input_data: Request data with 'action' key

        Returns:
            Processing results
        """
        action = input_data.get("action")

        if action == "daily_plan":
            return await self.create_daily_plan(input_data.get("date"))
        elif action == "weekly_plan":
            return await self.create_weekly_plan()
        elif action == "optimize_schedule":
            return await self.optimize_schedule(input_data)
        else:
            return {"success": False, "error": f"Unknown action: {action}"}

    async def create_daily_plan(self, date: str = None) -> Dict[str, Any]:
        """
        Create an optimized daily plan.

        Args:
            date: Target date (default: today)

        Returns:
            Daily plan
        """
        try:
            target_date = date or datetime.utcnow().date().isoformat()

            # Get calendar events
            calendar_result = await self.calendar_agent.sync_events(days_ahead=1)
            events = calendar_result.get("events", [])

            # Get tasks due soon
            task_result = await self.task_manager.get_tasks_due_soon(days=1)
            tasks = task_result.get("tasks", [])

            # Build comprehensive plan using AI
            system_prompt = """You are a daily planning assistant. Create an optimal
            daily schedule that:
            1. Integrates calendar events and tasks
            2. Prioritizes based on deadlines and importance
            3. Includes buffer time and breaks
            4. Balances focused work with meetings
            5. Suggests realistic time blocks"""

            events_summary = "\n".join(
                [f"- {e['summary']}: {e['start_time']} to {e['end_time']}" for e in events]
            ) or "No calendar events"

            tasks_summary = "\n".join(
                [
                    f"- {t['title']} (Priority: {t['priority']}, Due: {t.get('due_date', 'TBD')})"
                    for t in tasks
                ]
            ) or "No pending tasks"

            prompt = f"""Create an optimized daily plan for {target_date}

CALENDAR EVENTS:
{events_summary}

TASKS TO SCHEDULE:
{tasks_summary}

Create a hour-by-hour schedule from 8 AM to 6 PM. Include:
- All calendar events
- Time blocks for high-priority tasks
- Breaks and buffer time
- Realistic expectations for what can be accomplished"""

            plan = await self.call_llm(prompt, system_prompt, max_tokens=2048)

            return {
                "success": True,
                "date": target_date,
                "plan": plan,
                "events_count": len(events),
                "tasks_count": len(tasks),
            }

        except Exception as e:
            logger.error(f"Error creating daily plan: {e}")
            return {"success": False, "error": str(e)}

    async def create_weekly_plan(self) -> Dict[str, Any]:
        """
        Create a weekly plan overview.

        Returns:
            Weekly plan
        """
        try:
            # Get calendar events for the week
            calendar_result = await self.calendar_agent.sync_events(days_ahead=7)
            events = calendar_result.get("events", [])

            # Get upcoming tasks
            task_result = await self.task_manager.get_tasks_due_soon(days=7)
            tasks = task_result.get("tasks", [])

            system_prompt = """You are a weekly planning assistant. Create a strategic
            weekly overview that:
            1. Identifies key priorities and goals
            2. Distributes tasks across the week
            3. Highlights important meetings and deadlines
            4. Suggests focus areas for each day
            5. Identifies potential scheduling conflicts"""

            events_by_day = {}
            for event in events:
                # Group events by day
                # TODO: Parse and group by actual date
                pass

            events_summary = "\n".join(
                [
                    f"- {e['summary']} on {e['start_time'][:10]}: {e['start_time']} to {e['end_time']}"
                    for e in events
                ]
            ) or "No calendar events"

            tasks_summary = "\n".join(
                [
                    f"- {t['title']} (Priority: {t['priority']}, Due: {t.get('due_date', 'TBD')})"
                    for t in tasks
                ]
            ) or "No pending tasks"

            prompt = f"""Create a strategic weekly plan

UPCOMING EVENTS ({len(events)} total):
{events_summary[:1500]}

TASKS TO COMPLETE ({len(tasks)} total):
{tasks_summary[:1500]}

Provide:
1. Week overview with key themes/priorities
2. Day-by-day focus areas
3. Important deadlines and milestones
4. Recommendations for task distribution"""

            plan = await self.call_llm(prompt, system_prompt, max_tokens=3000)

            return {
                "success": True,
                "week_start": datetime.utcnow().date().isoformat(),
                "plan": plan,
                "events_count": len(events),
                "tasks_count": len(tasks),
            }

        except Exception as e:
            logger.error(f"Error creating weekly plan: {e}")
            return {"success": False, "error": str(e)}

    async def optimize_schedule(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze and optimize existing schedule.

        Args:
            params: Optimization parameters

        Returns:
            Optimization suggestions
        """
        try:
            # Get current schedule
            calendar_result = await self.calendar_agent.sync_events(days_ahead=7)
            events = calendar_result.get("events", [])

            system_prompt = """You are a schedule optimization assistant. Analyze
            the current schedule and suggest improvements:
            1. Identify time conflicts or overbooked periods
            2. Suggest better time blocks for focus work
            3. Recommend consolidating similar tasks
            4. Identify opportunities for delegation or elimination
            5. Propose better work-life balance"""

            events_summary = "\n".join(
                [
                    f"- {e['summary']}: {e['start_time']} to {e['end_time']}"
                    for e in events
                ]
            )

            prompt = f"""Analyze this schedule and suggest optimizations:

{events_summary}

Provide specific, actionable recommendations."""

            suggestions = await self.call_llm(prompt, system_prompt, max_tokens=2048)

            return {
                "success": True,
                "suggestions": suggestions,
                "events_analyzed": len(events),
            }

        except Exception as e:
            logger.error(f"Error optimizing schedule: {e}")
            return {"success": False, "error": str(e)}
