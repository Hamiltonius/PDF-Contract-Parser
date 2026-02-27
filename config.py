"""Configuration management for LifeOS."""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "LifeOS"
    app_version: str = "1.0.0"
    debug: bool = False

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = False

    # Database
    database_url: str = "sqlite:///./lifeos.db"

    # AI Provider (Claude by default)
    ai_provider: str = "anthropic"
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    claude_model: str = "claude-3-5-sonnet-20241022"

    # Google Calendar
    google_credentials_file: Optional[str] = None
    google_token_file: str = "token.json"

    # Email
    email_server: Optional[str] = None
    email_port: int = 993
    email_username: Optional[str] = None
    email_password: Optional[str] = None
    email_use_ssl: bool = True

    # Redis (for task queue)
    redis_url: str = "redis://localhost:6379/0"

    # File Storage
    upload_dir: Path = Path("uploads")
    max_upload_size: int = 10 * 1024 * 1024  # 10MB

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def get_settings() -> Settings:
    """Get application settings singleton."""
    return Settings()


# Create upload directory if it doesn't exist
settings = get_settings()
settings.upload_dir.mkdir(parents=True, exist_ok=True)
