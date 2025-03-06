"""
Database model for Meeting data.
"""

from datetime import datetime
from typing import List

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
    JSON,
    Table,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.db.base_class import Base


# Association table for the many-to-many relationship between Meeting and Attendee
meeting_attendee = Table(
    "meeting_attendee",
    Base.metadata,
    Column("meeting_id", Integer, ForeignKey("meetings.id"), primary_key=True),
    Column("attendee_id", Integer, ForeignKey("attendees.id"), primary_key=True),
)


class Meeting(Base):
    """
    Meeting database model for storing meeting data from webhooks.

    Attributes:
        id: Unique identifier
        name: Meeting name
        created_at: When the meeting was created
        duration: Duration of the meeting in seconds
        url: URL of the meeting
        recording_url: URL of the recording
        notes: Meeting notes in markdown format
        external_id: External ID from the source system
        received_at: When the webhook was received
    """

    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    duration = Column(Float, nullable=True)
    url = Column(String(1024), nullable=True)
    recording_url = Column(String(2048), nullable=True)
    notes = Column(Text, nullable=True)
    external_id = Column(Integer, nullable=True, index=True)
    received_at = Column(DateTime(timezone=True), server_default="now()")

    # Relationships
    attendees = relationship(
        "Attendee", secondary=meeting_attendee, back_populates="meetings"
    )
    action_items = relationship(
        "ActionItem", back_populates="meeting", cascade="all, delete-orphan"
    )
    transcript_entries = relationship(
        "TranscriptEntry", back_populates="meeting", cascade="all, delete-orphan"
    )


class Attendee(Base):
    """
    Attendee database model for storing unique attendees across meetings.

    Attributes:
        id: Unique identifier
        name: Attendee name
        email: Attendee email (unique)
    """

    __tablename__ = "attendees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True, unique=True, index=True)

    # Relationships
    meetings = relationship(
        "Meeting", secondary=meeting_attendee, back_populates="attendees"
    )

    # Add UniqueConstraint to ensure email is unique when not null
    __table_args__ = (UniqueConstraint("email", name="uix_attendee_email"),)


class ActionItem(Base):
    """
    ActionItem database model for storing meeting action items.

    Attributes:
        id: Unique identifier
        title: Action item title
        description: Action item description
        status: Action item status (e.g., PENDING, COMPLETED)
        assignee_name: Name of the person assigned to the action item
        assignee_email: Email of the person assigned to the action item
        external_id: External ID from the source system
        meeting_id: Foreign key to the meeting
    """

    __tablename__ = "action_items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="PENDING")
    assignee_name = Column(String(255), nullable=True)
    assignee_email = Column(String(255), nullable=True)
    external_id = Column(Integer, nullable=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=False)

    # Relationships
    meeting = relationship("Meeting", back_populates="action_items")


class TranscriptEntry(Base):
    """
    TranscriptEntry database model for storing meeting transcript entries.

    Attributes:
        id: Unique identifier
        speaker: Name of the speaker
        text: Transcript text
        timestamp: Timestamp in seconds from the start of the meeting
        meeting_id: Foreign key to the meeting
    """

    __tablename__ = "transcript_entries"

    id = Column(Integer, primary_key=True, index=True)
    speaker = Column(String(255), nullable=False)
    text = Column(Text, nullable=False)
    timestamp = Column(Float, nullable=False)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=False)

    # Relationships
    meeting = relationship("Meeting", back_populates="transcript_entries")


class DenormalizedMeetingView(Base):
    """
    Denormalized view of meeting data for faster exports.
    This table contains pre-processed data to avoid expensive joins at export time.

    Attributes:
        id: Unique identifier (same as the original meeting id)
        name: Meeting name
        created_at: When the meeting was created
        duration: Duration of the meeting in seconds
        url: URL of the meeting
        recording_url: URL of the recording
        notes: Meeting notes in markdown format
        external_id: External ID from the source system
        received_at: When the webhook was received
        attendees_data: JSON representation of attendees
        action_items_data: JSON representation of action items
        transcript_data: JSON representation of the transcript, with formatted timestamps
        last_updated: When this denormalized view was last updated
    """

    __tablename__ = "denormalized_meetings_view"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    duration = Column(Float, nullable=True)
    url = Column(String(1024), nullable=True)
    recording_url = Column(String(2048), nullable=True)
    notes = Column(Text, nullable=True)
    external_id = Column(Integer, nullable=True, index=True)
    received_at = Column(DateTime(timezone=True))
    attendees_data = Column(JSON, nullable=True)
    action_items_data = Column(JSON, nullable=True)
    transcript_data = Column(JSON, nullable=True)
    last_updated = Column(DateTime(timezone=True), server_default="now()")
