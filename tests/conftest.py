"""
Shared test fixtures for the meetings app.
"""

import asyncio
import pytest
from datetime import datetime, timedelta
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base_class import Base
from app.db.session import get_db
from app.models.meeting import Meeting, Attendee, ActionItem, TranscriptEntry, DenormalizedMeetingView
from app.schemas.meeting import WebhookPayload, AttendeeCreate, ActionItemCreate, TranscriptEntryCreate
from app.core.app import create_app


@pytest.fixture(scope="session")
def db_engine():
    """Create a SQLAlchemy engine for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create a SQLAlchemy session for testing."""
    # Create a new connection
    connection = db_engine.connect()
    # Begin a non-ORM transaction
    transaction = connection.begin()
    
    # Bind a session to the connection
    Session = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = Session()
    
    try:
        yield session
    finally:
        # Roll back the transaction and close the connection
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def app(db_session):
    """Create a FastAPI app for testing."""
    app = create_app()
    
    # Override the get_db dependency
    async def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    return app


@pytest.fixture(scope="function")
def client(app):
    """Create a test client for the FastAPI app."""
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="function")
def sample_meeting_data():
    """Create sample meeting data for testing."""
    return {
        "id": 123,
        "name": "Test Meeting",
        "createdAt": datetime.now().isoformat(),
        "duration": 3600,
        "url": "https://example.com/meeting/123",
        "attendees": [
            {"name": "John Doe", "email": "john@example.com"},
            {"name": "Jane Smith", "email": "jane@example.com"},
        ],
        "recordingUrl": "https://example.com/recording/123",
        "notes": "# Meeting Notes\n\nThis is a test meeting with notes in markdown format.",
        "actionItems": [
            {
                "title": "Research new feature",
                "description": "Look into implementing the new feature",
                "status": "PENDING",
                "assignee_name": "John Doe",
                "assignee_email": "john@example.com",
            }
        ],
        "transcript": [
            {
                "speaker": "John Doe",
                "text": "Hello everyone, welcome to the meeting.",
                "timestamp": 0.0,
            },
            {
                "speaker": "Jane Smith",
                "text": "Thanks for organizing this, John.",
                "timestamp": 10.5,
            },
        ],
    }


@pytest.fixture(scope="function")
def background_tasks_mock():
    """Create a mock for background tasks."""
    class BackgroundTasksMock:
        def __init__(self):
            self.tasks = []
        
        def add_task(self, func, *args, **kwargs):
            self.tasks.append((func, args, kwargs))
            
    return BackgroundTasksMock()


@pytest.fixture(scope="function")
def db_meeting(db_session):
    """Create a test meeting in the database."""
    # Create a meeting
    meeting = Meeting(
        name="Test Meeting",
        created_at=datetime.now(),
        duration=3600,
        url="https://example.com/meeting/1",
        recording_url="https://example.com/recording/1",
        notes="# Test Meeting\n\nTest notes",
        external_id=1,
        received_at=datetime.now(),
    )
    db_session.add(meeting)
    
    # Create attendees
    attendee1 = Attendee(name="John Doe", email="john@example.com")
    attendee2 = Attendee(name="Jane Smith", email="jane@example.com")
    db_session.add_all([attendee1, attendee2])
    db_session.flush()
    
    # Associate attendees with meeting
    meeting.attendees.append(attendee1)
    meeting.attendees.append(attendee2)
    
    # Add action items
    action_item = ActionItem(
        title="Test Action Item",
        description="This is a test action item",
        status="PENDING",
        assignee_name="John Doe",
        assignee_email="john@example.com",
        meeting_id=meeting.id,
    )
    db_session.add(action_item)
    
    # Add transcript entries
    transcript_entry1 = TranscriptEntry(
        speaker="John Doe",
        text="Hello, this is a test meeting.",
        timestamp=0.0,
        meeting_id=meeting.id,
    )
    transcript_entry2 = TranscriptEntry(
        speaker="Jane Smith",
        text="Thank you for organizing this meeting.",
        timestamp=10.0,
        meeting_id=meeting.id,
    )
    db_session.add_all([transcript_entry1, transcript_entry2])
    
    # Commit
    db_session.commit()
    db_session.refresh(meeting)
    
    return meeting