"""Database initialization and management."""
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import get_settings
from database.models import Base

logger = logging.getLogger(__name__)


def init_database():
    """Initialize the database and create all tables."""
    settings = get_settings()

    # Create engine
    engine = create_engine(
        settings.database_url,
        echo=settings.debug,
        connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")

    return engine


def get_db_session():
    """Get a database session."""
    settings = get_settings()
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()
