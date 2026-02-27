"""Email processing agent."""
import logging
from typing import Any, Dict, List

from agents.base_agent import BaseAgent
from ingestion.email_sync import EmailSync

logger = logging.getLogger(__name__)


class EmailAgent(BaseAgent):
    """Agent for email processing and task extraction."""

    def __init__(self):
        """Initialize email agent."""
        super().__init__("EmailAgent")
        self.email_sync = EmailSync()

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process email-related request.

        Args:
            input_data: Request data with 'action' key

        Returns:
            Processing results
        """
        action = input_data.get("action")

        if action == "sync_emails":
            return await self.sync_emails(input_data.get("limit", 50))
        elif action == "extract_tasks":
            return await self.extract_tasks_from_emails(input_data.get("email_ids", []))
        elif action == "summarize_unread":
            return await self.summarize_unread_emails()
        elif action == "draft_reply":
            return await self.draft_reply(input_data)
        else:
            return {"success": False, "error": f"Unknown action: {action}"}

    async def sync_emails(self, limit: int = 50) -> Dict[str, Any]:
        """
        Sync recent emails.

        Args:
            limit: Maximum number of emails to sync

        Returns:
            Sync results
        """
        try:
            emails = self.email_sync.get_recent_emails(limit=limit)
            self.email_sync.disconnect()

            self.log_action(
                "sync_emails",
                input_data={"limit": limit},
                output_data={"email_count": len(emails)},
                success=True,
            )

            return {
                "success": True,
                "email_count": len(emails),
                "emails": emails,
            }

        except Exception as e:
            logger.error(f"Error syncing emails: {e}")
            self.log_action(
                "sync_emails",
                input_data={"limit": limit},
                success=False,
                error=str(e),
            )
            return {"success": False, "error": str(e)}

    async def extract_tasks_from_emails(self, email_ids: List[str]) -> Dict[str, Any]:
        """
        Extract actionable tasks from emails using AI.

        Args:
            email_ids: List of email IDs to process

        Returns:
            Extracted tasks
        """
        try:
            # For demo, we'll process recent unread emails
            emails = self.email_sync.get_unread_emails()
            self.email_sync.disconnect()

            if not emails:
                return {"success": True, "tasks": [], "message": "No unread emails"}

            tasks = []

            for email_data in emails[:5]:  # Process first 5 for demo
                task_result = await self._extract_tasks_from_single_email(email_data)
                if task_result:
                    tasks.extend(task_result)

            return {
                "success": True,
                "task_count": len(tasks),
                "tasks": tasks,
            }

        except Exception as e:
            logger.error(f"Error extracting tasks from emails: {e}")
            return {"success": False, "error": str(e)}

    async def _extract_tasks_from_single_email(
        self, email_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract tasks from a single email."""
        try:
            system_prompt = """You are an email task extractor. Analyze emails and
            identify actionable items, deadlines, and requests. Return tasks in this format:

            TASK: [task description]
            DUE: [due date if mentioned, or "None"]
            PRIORITY: [1-5, based on urgency indicators]
            ---

            Only extract clear action items. Ignore informational content."""

            prompt = f"""Email from: {email_data['sender']}
Subject: {email_data['subject']}

Body:
{email_data['body'][:1000]}

Extract all actionable tasks from this email."""

            response = await self.call_llm(prompt, system_prompt, max_tokens=1024)

            # Parse response and create task objects
            # TODO: Parse AI response into structured tasks
            # For now, return raw response

            if "TASK:" in response:
                return [
                    {
                        "title": f"Task from: {email_data['subject']}",
                        "description": response,
                        "source": "email",
                        "source_id": email_data.get("message_id"),
                    }
                ]

            return []

        except Exception as e:
            logger.error(f"Error extracting tasks from email: {e}")
            return []

    async def summarize_unread_emails(self) -> Dict[str, Any]:
        """
        Summarize unread emails using AI.

        Returns:
            Email summary
        """
        try:
            emails = self.email_sync.get_unread_emails()
            self.email_sync.disconnect()

            if not emails:
                return {"success": True, "summary": "No unread emails"}

            email_summaries = "\n\n".join(
                [
                    f"From: {e['sender']}\nSubject: {e['subject']}\n{e['body'][:200]}..."
                    for e in emails[:10]
                ]
            )

            system_prompt = """You are an email summarization assistant. Provide a
            concise summary of unread emails, highlighting:
            1. Urgent items requiring immediate attention
            2. Important updates or decisions needed
            3. Informational emails that can be read later"""

            prompt = f"""Summarize these {len(emails)} unread emails:\n\n{email_summaries}"""

            response = await self.call_llm(prompt, system_prompt, max_tokens=2048)

            return {
                "success": True,
                "unread_count": len(emails),
                "summary": response,
            }

        except Exception as e:
            logger.error(f"Error summarizing emails: {e}")
            return {"success": False, "error": str(e)}

    async def draft_reply(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Draft an email reply using AI.

        Args:
            params: Reply parameters (email content, tone, key points)

        Returns:
            Drafted reply
        """
        try:
            original_email = params.get("original_email", "")
            tone = params.get("tone", "professional")
            key_points = params.get("key_points", "")

            system_prompt = f"""You are an email drafting assistant. Write a {tone}
            email reply that addresses the key points provided. Keep it concise
            and clear."""

            prompt = f"""Original email:\n{original_email}\n\n
            Key points to address:\n{key_points}\n\n
            Draft a reply."""

            response = await self.call_llm(prompt, system_prompt, max_tokens=1024)

            return {
                "success": True,
                "draft": response,
            }

        except Exception as e:
            logger.error(f"Error drafting reply: {e}")
            return {"success": False, "error": str(e)}
