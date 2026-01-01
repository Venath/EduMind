from typing import Generator

from app.core.config import settings
from app.db.base import get_db_session

# Handle optional DATABASE_URL
if settings.DATABASE_URL:
    SessionLocal = get_db_session(settings.DATABASE_URL)
else:
    SessionLocal = None


def get_db() -> Generator:
    """Dependency for getting DB session"""
    if SessionLocal is None:
        raise RuntimeError("Database not configured")
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
