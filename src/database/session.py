"""Database session management"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator
import logging

from ..config import get_settings
from .models import Base

logger = logging.getLogger(__name__)

# Global engine and session factory
_engine = None
_SessionLocal = None


def init_db():
    """Initialize database and create tables"""
    global _engine, _SessionLocal

    settings = get_settings()
    database_url = settings.database.url

    logger.info(f"Initializing database: {database_url}")

    _engine = create_engine(
        database_url,
        pool_size=settings.database.pool_size,
        echo=settings.database.echo
    )

    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)

    # Create all tables
    Base.metadata.create_all(bind=_engine)

    logger.info("Database initialized successfully")


def get_engine():
    """Get database engine"""
    global _engine
    if _engine is None:
        init_db()
    return _engine


def get_session_factory():
    """Get session factory"""
    global _SessionLocal
    if _SessionLocal is None:
        init_db()
    return _SessionLocal


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Get database session with context manager.

    Usage:
        with get_db() as db:
            db.query(ValidationHistory).all()
    """
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        db.close()


def get_db_session() -> Session:
    """
    Get database session (for FastAPI dependency injection).

    Usage in FastAPI:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db_session)):
            return db.query(Item).all()
    """
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
