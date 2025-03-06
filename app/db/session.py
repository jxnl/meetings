"""
Database session configuration using SQLAlchemy.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Use the DIRECT_URL for database connections
# This bypasses pgbouncer and connects directly to the database
engine = create_engine(
    settings.DIRECT_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Verify connections before using them
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db():
    """
    Get database session.

    Yields:
        Session: Database session

    Notes:
        This function is used as a dependency in FastAPI endpoints.
        It creates a new database session for each request and closes it when done.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
