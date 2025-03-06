"""
Script to initialize the database.

This script drops all existing tables and recreates them.
"""

import logging
import time

from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError, ProgrammingError

from app.db.session import engine
from app.db.base import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db() -> None:
    """
    Initialize the database by dropping all tables and recreating them.

    This function drops all existing tables and recreates them based on the models.
    """
    try:
        # Get existing tables
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()

        # Log existing tables
        if existing_tables:
            logger.info("Existing tables: %s", existing_tables)

            # Use raw SQL to drop all tables with CASCADE option
            logger.info("Dropping all tables with CASCADE option...")
            with engine.begin() as conn:
                # Disable foreign key checks temporarily
                conn.execute(text("SET CONSTRAINTS ALL DEFERRED"))

                # First drop any potential foreign key constraints
                logger.info("Dropping foreign key constraints...")
                conn.execute(
                    text(
                        """
                    DO $$ 
                    DECLARE
                        r RECORD;
                    BEGIN
                        FOR r IN (SELECT conname, conrelid::regclass AS table_name FROM pg_constraint WHERE contype = 'f') 
                        LOOP
                            EXECUTE 'ALTER TABLE ' || r.table_name || ' DROP CONSTRAINT IF EXISTS ' || r.conname;
                        END LOOP;
                    END $$;
                """
                    )
                )

                # Drop each table with CASCADE
                for table in existing_tables:
                    logger.info(f"Dropping table {table}...")
                    conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))

            logger.info("All tables dropped successfully")

            # Verify tables were dropped
            inspector = inspect(engine)
            remaining_tables = inspector.get_table_names()
            if remaining_tables:
                logger.warning(
                    "Some tables still exist after drop attempt: %s", remaining_tables
                )
                # Try one more time with a more aggressive approach
                logger.info("Attempting to drop remaining tables again...")
                with engine.begin() as conn:
                    for table in remaining_tables:
                        logger.info(f"Force dropping table {table}...")
                        try:
                            conn.execute(text(f'DROP TABLE "{table}" CASCADE'))
                        except Exception as e:
                            logger.error(f"Could not drop table {table}: {str(e)}")
        else:
            logger.info("No existing tables found")

        # Create tables
        logger.info("Creating tables...")
        try:
            Base.metadata.create_all(bind=engine)
        except ProgrammingError as e:
            if "already exists" in str(e):
                logger.warning("Tables already exist. Attempting to recreate...")
                # Wait a moment for any transactions to complete
                time.sleep(1)
                # Try to drop again and recreate
                with engine.begin() as conn:
                    for table in inspector.get_table_names():
                        conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
                # Now try to create again
                Base.metadata.create_all(bind=engine)
            else:
                raise

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
