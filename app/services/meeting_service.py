"""
Service for handling meeting data operations.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session

from app.models.meeting import Meeting, Attendee, ActionItem, TranscriptEntry
from app.schemas.meeting import MeetingCreate, WebhookPayload


def create_meeting_from_webhook(db: Session, payload: WebhookPayload) -> Meeting:
    """
    Create a meeting record from a webhook payload.

    Args:
        db: Database session
        payload: Webhook payload data

    Returns:
        Meeting: Created meeting object
    """
    # Create meeting object
    db_meeting = Meeting(
        name=payload.name,
        created_at=payload.createdAt,
        duration=payload.duration,
        url=payload.url,
        recording_url=payload.recordingUrl,
        notes=payload.notes,
        external_id=payload.id,
        received_at=datetime.now(),
    )

    # Add to session
    db.add(db_meeting)
    db.flush()  # Flush to get the meeting ID

    # Create attendees
    if payload.attendees:
        for attendee_data in payload.attendees:
            db_attendee = Attendee(
                name=attendee_data.name,
                email=attendee_data.email,
                meeting_id=db_meeting.id,
            )
            db.add(db_attendee)

    # Create action items
    if payload.actionItems:
        for item_data in payload.actionItems:
            db_action_item = ActionItem(
                title=item_data.title,
                description=item_data.description,
                status=item_data.status,
                assignee_name=item_data.assignee_name,
                assignee_email=item_data.assignee_email,
                external_id=item_data.external_id,
                meeting_id=db_meeting.id,
            )
            db.add(db_action_item)

    # Create transcript entries
    if payload.transcript:
        for entry_data in payload.transcript:
            db_transcript = TranscriptEntry(
                speaker=entry_data.speaker,
                text=entry_data.text,
                timestamp=entry_data.timestamp,
                meeting_id=db_meeting.id,
            )
            db.add(db_transcript)

    # Commit the transaction
    db.commit()
    db.refresh(db_meeting)

    return db_meeting


def get_meeting(db: Session, meeting_id: int) -> Optional[Meeting]:
    """
    Get a meeting by ID.

    Args:
        db: Database session
        meeting_id: Meeting ID

    Returns:
        Meeting: Meeting object if found, None otherwise
    """
    return db.query(Meeting).filter(Meeting.id == meeting_id).first()


def get_meetings(db: Session, skip: int = 0, limit: int = 100) -> List[Meeting]:
    """
    Get a list of meetings.

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List[Meeting]: List of meeting objects
    """
    return (
        db.query(Meeting)
        .order_by(Meeting.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_meeting_by_external_id(db: Session, external_id: int) -> Optional[Meeting]:
    """
    Get a meeting by its external ID.

    Args:
        db: Database session
        external_id: External ID from the source system

    Returns:
        Meeting: Meeting object if found, None otherwise
    """
    return db.query(Meeting).filter(Meeting.external_id == external_id).first()


def delete_meeting(db: Session, meeting_id: int) -> bool:
    """
    Delete a meeting by ID.

    Args:
        db: Database session
        meeting_id: Meeting ID

    Returns:
        bool: True if deleted, False if not found
    """
    db_meeting = get_meeting(db, meeting_id)
    if db_meeting:
        db.delete(db_meeting)
        db.commit()
        return True
    return False
