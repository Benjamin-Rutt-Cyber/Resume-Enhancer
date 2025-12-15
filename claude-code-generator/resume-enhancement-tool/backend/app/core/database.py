"""Database configuration and session management."""

import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import settings

logger = logging.getLogger(__name__)

# Create SQLAlchemy engine
# Add connect_args for SQLite compatibility
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db():
    """
    Dependency function to get database session.

    Yields:
        Database session

    Raises:
        Exception: Re-raises any exception after rolling back the transaction
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        # Rollback on any error to prevent partial commits
        db.rollback()
        logger.error(f"Database error occurred: {e}", exc_info=True)
        raise
    finally:
        db.close()
