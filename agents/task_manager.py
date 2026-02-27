"""Task management agent."""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from agents.base_agent import BaseAgent
from database.init_db import get_db_session
from database.models import Task

logger = logging.getLogger(__name__)


class TaskManagerAgent(BaseAgent):
    """Agent for managing tasks and priorities."""

    def __init__(self):
        """Initialize task manager agent."""
        super().__init__("TaskManager")

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process task management request.

        Args:
            input_data: Request data with 'action' key

        Returns:
            Processing results
        """
        action = input_data.get("action")

        if action == "create_task":
            return await self.create_task(input_data)
        elif action == "prioritize_tasks":
            return await self.prioritize_tasks()
        elif action == "get_due_soon":
            return await self.get_tasks_due_soon(input_data.get("days", 3))
        elif action == "suggest_schedule":
            return await self.suggest_schedule(input_data.get("date"))
        else:
            return {"success": False, "error": f"Unknown action: {action}"}

    async def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new task.

        Args:
            task_data: Task information

        Returns:
            Created task data
        """
        try:
            db = get_db_session()

            task = Task(
                title=task_data.get("title"),
                description=task_data.get("description"),
                status="pending",
                priority=task_data.get("priority", 3),
                due_date=task_data.get("due_date"),
                source=task_data.get("source", "manual"),
                estimated_duration=task_data.get("estimated_duration"),
            )

            db.add(task)
            db.commit()
            db.refresh(task)

            logger.info(f"Created task: {task.title}")

            return {
                "success": True,
                "task_id": task.id,
                "task": {
                    "id": task.id,
                    "title": task.title,
                    "status": task.status,
                    "priority": task.priority,
                },
            }

        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return {"success": False, "error": str(e)}

    async def prioritize_tasks(self) -> Dict[str, Any]:
        """
        Use AI to prioritize pending tasks.

        Returns:
            Prioritized task list
        """
        try:
            db = get_db_session()
            tasks = db.query(Task).filter(Task.status == "pending").all()

            if not tasks:
                return {"success": True, "tasks": [], "message": "No pending tasks"}

            # Build prompt for AI
            task_list = "\n".join(
                [
                    f"- {task.title} (Due: {task.due_date or 'No due date'}, "
                    f"Current Priority: {task.priority})"
                    for task in tasks
                ]
            )

            system_prompt = """You are a task prioritization assistant.
            Analyze tasks and assign priorities from 1 (highest) to 5 (lowest) based on:
            - Urgency (due dates)
            - Importance
            - Dependencies
            - Estimated effort

            Return priorities as: TaskTitle: Priority (1-5)"""

            prompt = f"""Prioritize these tasks:\n\n{task_list}\n\n
            Provide priority (1-5) for each task with brief reasoning."""

            response = await self.call_llm(prompt, system_prompt, max_tokens=2048)

            # TODO: Parse response and update task priorities

            return {
                "success": True,
                "tasks": [{"id": t.id, "title": t.title, "priority": t.priority} for t in tasks],
                "ai_suggestions": response,
            }

        except Exception as e:
            logger.error(f"Error prioritizing tasks: {e}")
            return {"success": False, "error": str(e)}

    async def get_tasks_due_soon(self, days: int = 3) -> Dict[str, Any]:
        """
        Get tasks due within specified days.

        Args:
            days: Number of days to look ahead

        Returns:
            List of upcoming tasks
        """
        try:
            db = get_db_session()
            cutoff_date = datetime.utcnow() + timedelta(days=days)

            tasks = (
                db.query(Task)
                .filter(
                    Task.status.in_(["pending", "in_progress"]),
                    Task.due_date <= cutoff_date,
                )
                .order_by(Task.due_date)
                .all()
            )

            return {
                "success": True,
                "count": len(tasks),
                "tasks": [
                    {
                        "id": t.id,
                        "title": t.title,
                        "due_date": t.due_date.isoformat() if t.due_date else None,
                        "priority": t.priority,
                        "status": t.status,
                    }
                    for t in tasks
                ],
            }

        except Exception as e:
            logger.error(f"Error getting due soon tasks: {e}")
            return {"success": False, "error": str(e)}

    async def suggest_schedule(self, date: Optional[str] = None) -> Dict[str, Any]:
        """
        Suggest an optimal schedule for tasks.

        Args:
            date: Target date (default: today)

        Returns:
            Suggested schedule
        """
        try:
            # Get pending tasks
            db = get_db_session()
            tasks = db.query(Task).filter(Task.status == "pending").limit(10).all()

            if not tasks:
                return {"success": True, "schedule": [], "message": "No tasks to schedule"}

            # Build AI prompt
            task_info = "\n".join(
                [
                    f"- {task.title} (Priority: {task.priority}, "
                    f"Est. Duration: {task.estimated_duration or 'unknown'} min)"
                    for task in tasks
                ]
            )

            system_prompt = """You are a scheduling assistant. Create an optimal
            daily schedule considering task priorities, estimated durations, and
            work-life balance. Suggest time blocks for each task."""

            prompt = f"""Create a schedule for these tasks:\n\n{task_info}\n\n
            Assume an 8-hour workday (9 AM - 5 PM) with breaks."""

            response = await self.call_llm(prompt, system_prompt, max_tokens=2048)

            return {
                "success": True,
                "date": date or datetime.utcnow().date().isoformat(),
                "schedule": response,
                "tasks_included": len(tasks),
            }

        except Exception as e:
            logger.error(f"Error suggesting schedule: {e}")
            return {"success": False, "error": str(e)}
