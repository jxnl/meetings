"""
Script to initialize the database.

This script creates all tables defined in the models.
"""

import logging

from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import engine
from app.db.base import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db() -> None:
    """
    Initialize the database by creating all tables.

    This function creates all tables defined in the models if they don't exist.
    """
    try:
        # Get existing tables
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()

        # Log existing tables
        if existing_tables:
            logger.info("Existing tables: %s", existing_tables)
        else:
            logger.info("No existing tables found")

        # Create tables
        logger.info("Creating tables...")
        Base.metadata.create_all(bind=engine)

        # Get tables after creation
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.info("Tables after initialization: %s", tables)

        logger.info("Database initialization completed successfully")

    except SQLAlchemyError as e:
        logger.error("Database initialization failed: %s", str(e))
        raise


if __name__ == "__main__":
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialization completed")
