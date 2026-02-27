"""LifeOS - Personal AI Operating System (MVP v1)."""
import asyncio
import logging
from pathlib import Path

import uvicorn
from api.server import app
from config import get_settings
from database.init_db import init_database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def startup():
    """Initialize application on startup."""
    settings = get_settings()
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")

    # Initialize database
    logger.info("Initializing database...")
    init_database()
    logger.info("Database initialized successfully")

    # Create necessary directories
    Path("uploads").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)

    logger.info(f"Server starting on {settings.api_host}:{settings.api_port}")


def main():
    """Run the application."""
    settings = get_settings()

    # Run startup tasks
    asyncio.run(startup())

    # Start server
    uvicorn.run(
        "api.server:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level="info" if settings.debug else "warning",
    )


if __name__ == "__main__":
    main()
