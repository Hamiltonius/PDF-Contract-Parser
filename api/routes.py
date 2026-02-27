"""API routes for LifeOS."""
import logging
from pathlib import Path
from typing import Dict, Any, List

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

from agents.task_manager import TaskManagerAgent
from agents.calendar_agent import CalendarAgent
from agents.email_agent import EmailAgent
from agents.planner_agent import PlannerAgent
from ingestion.pdf_parser import PDFParser
from config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()

# Initialize agents
task_manager = TaskManagerAgent()
calendar_agent = CalendarAgent()
email_agent = EmailAgent()
planner_agent = PlannerAgent()
pdf_parser = PDFParser()


# Request/Response Models
class TaskCreate(BaseModel):
    title: str
    description: str = ""
    priority: int = 3
    due_date: str = None
    estimated_duration: int = None


class AgentRequest(BaseModel):
    action: str
    params: Dict[str, Any] = {}


# Task Management Endpoints
@router.post("/tasks/create")
async def create_task(task: TaskCreate):
    """Create a new task."""
    result = await task_manager.create_task(task.dict())
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@router.get("/tasks/due-soon")
async def get_tasks_due_soon(days: int = 3):
    """Get tasks due within specified days."""
    result = await task_manager.get_tasks_due_soon(days)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@router.post("/tasks/prioritize")
async def prioritize_tasks():
    """Prioritize pending tasks using AI."""
    result = await task_manager.prioritize_tasks()
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@router.post("/tasks/suggest-schedule")
async def suggest_schedule(date: str = None):
    """Get AI-suggested schedule for tasks."""
    result = await task_manager.suggest_schedule(date)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


# Calendar Endpoints
@router.post("/calendar/sync")
async def sync_calendar(days_ahead: int = 7):
    """Sync calendar events from Google Calendar."""
    result = await calendar_agent.sync_events(days_ahead)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@router.post("/calendar/find-free-time")
async def find_free_time(request: AgentRequest):
    """Find free time slots in calendar."""
    result = await calendar_agent.find_free_time(request.params)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@router.post("/calendar/suggest-meeting-times")
async def suggest_meeting_times(request: AgentRequest):
    """Suggest optimal meeting times."""
    result = await calendar_agent.suggest_meeting_times(request.params)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


# Email Endpoints
@router.post("/email/sync")
async def sync_emails(limit: int = 50):
    """Sync recent emails."""
    result = await email_agent.sync_emails(limit)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@router.post("/email/extract-tasks")
async def extract_tasks_from_emails(email_ids: List[str] = []):
    """Extract tasks from emails using AI."""
    result = await email_agent.extract_tasks_from_emails(email_ids)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@router.get("/email/summarize-unread")
async def summarize_unread_emails():
    """Summarize unread emails."""
    result = await email_agent.summarize_unread_emails()
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


# Planning Endpoints
@router.post("/planner/daily-plan")
async def create_daily_plan(date: str = None):
    """Create an optimized daily plan."""
    result = await planner_agent.create_daily_plan(date)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@router.post("/planner/weekly-plan")
async def create_weekly_plan():
    """Create a strategic weekly plan."""
    result = await planner_agent.create_weekly_plan()
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@router.post("/planner/optimize-schedule")
async def optimize_schedule(request: AgentRequest):
    """Get schedule optimization suggestions."""
    result = await planner_agent.optimize_schedule(request.params)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


# Document Processing Endpoints
@router.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document (PDF)."""
    try:
        # Save uploaded file
        file_path = settings.upload_dir / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Parse PDF if applicable
        if file.filename.endswith(".pdf"):
            result = pdf_parser.parse(file_path)
            if result.get("success"):
                return {
                    "success": True,
                    "filename": file.filename,
                    "file_path": str(file_path),
                    "page_count": result.get("page_count"),
                    "text_length": len(result.get("text", "")),
                }
            else:
                raise HTTPException(status_code=400, detail=result.get("error"))
        else:
            return {
                "success": True,
                "filename": file.filename,
                "file_path": str(file_path),
            }

    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.app_name} v{settings.app_version}",
        "docs": "/docs",
        "health": "/health",
    }
