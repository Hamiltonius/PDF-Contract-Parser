"""SQLAlchemy database models for LifeOS."""
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Document(Base):
    """Stored documents (PDFs, text files, etc.)."""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False)
    processed_date = Column(DateTime, nullable=True)
    extracted_text = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)

    # Relationships
    tasks = relationship("Task", back_populates="document")


class Task(Base):
    """Tasks extracted from documents or created by agents."""

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="pending")  # pending, in_progress, completed, cancelled
    priority = Column(Integer, default=3)  # 1=highest, 5=lowest
    due_date = Column(DateTime, nullable=True)
    created_date = Column(DateTime, default=datetime.utcnow)
    completed_date = Column(DateTime, nullable=True)
    source = Column(String(50), nullable=True)  # document, email, calendar, manual
    source_id = Column(Integer, nullable=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    calendar_event_id = Column(String(255), nullable=True)
    email_id = Column(String(255), nullable=True)
    estimated_duration = Column(Integer, nullable=True)  # minutes
    metadata = Column(JSON, nullable=True)

    # Relationships
    document = relationship("Document", back_populates="tasks")


class CalendarEvent(Base):
    """Calendar events synced from Google Calendar."""

    __tablename__ = "calendar_events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(255), unique=True, nullable=False)
    calendar_id = Column(String(255), nullable=False)
    summary = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    location = Column(String(500), nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    all_day = Column(Boolean, default=False)
    status = Column(String(50), nullable=True)
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, nullable=True)
    metadata = Column(JSON, nullable=True)


class Email(Base):
    """Emails synced from email server."""

    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String(255), unique=True, nullable=False)
    subject = Column(String(500), nullable=True)
    sender = Column(String(255), nullable=False)
    recipients = Column(Text, nullable=True)  # JSON array
    body = Column(Text, nullable=True)
    received_date = Column(DateTime, nullable=False)
    read = Column(Boolean, default=False)
    flagged = Column(Boolean, default=False)
    folder = Column(String(100), default="INBOX")
    has_attachments = Column(Boolean, default=False)
    processed = Column(Boolean, default=False)
    metadata = Column(JSON, nullable=True)


class AgentLog(Base):
    """Logs of agent actions and decisions."""

    __tablename__ = "agent_logs"

    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String(100), nullable=False)
    action = Column(String(255), nullable=False)
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    execution_time = Column(Float, nullable=True)  # seconds
    timestamp = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON, nullable=True)
