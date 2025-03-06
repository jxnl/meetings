"""
Service for handling meeting data operations.
"""

from datetime import datetime, timedelta
import json
from typing import List, Optional, Dict, Any, Tuple

from sqlalchemy import func, case, and_
from sqlalchemy.orm import Session

from app.models.meeting import (
    Meeting,
    Attendee,
    ActionItem,
    TranscriptEntry,
    DenormalizedMeetingView,
)
from app.schemas.meeting import (
    MeetingCreate,
    WebhookPayload,
    DenormalizedMeeting,
    DenormalizedAttendee,
    DenormalizedActionItem,
    DenormalizedTranscriptEntry,
)


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

    # Process attendees
    if payload.attendees:
        for attendee_data in payload.attendees:
            # Skip attendees without email
            if not attendee_data.email:
                continue

            # Find existing attendee by email or create a new one
            existing_attendee = (
                db.query(Attendee).filter(Attendee.email == attendee_data.email).first()
            )

            if existing_attendee:
                # Update name if needed (use most recent name)
                if existing_attendee.name != attendee_data.name:
                    existing_attendee.name = attendee_data.name

                # Add meeting to existing attendee
                existing_attendee.meetings.append(db_meeting)
            else:
                # Create new attendee
                new_attendee = Attendee(
                    name=attendee_data.name,
                    email=attendee_data.email,
                )
                db.add(new_attendee)
                db.flush()  # Flush to get the attendee ID

                # Add meeting to new attendee
                new_attendee.meetings.append(db_meeting)

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


def get_attendee_by_email(db: Session, email: str) -> Optional[Attendee]:
    """
    Get an attendee by email.

    Args:
        db: Database session
        email: Attendee email

    Returns:
        Attendee: Attendee object if found, None otherwise
    """
    return db.query(Attendee).filter(Attendee.email == email).first()


def get_attendees(db: Session, skip: int = 0, limit: int = 100) -> List[Attendee]:
    """
    Get a list of unique attendees.

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List[Attendee]: List of attendee objects
    """
    return db.query(Attendee).offset(skip).limit(limit).all()


def get_attendees_with_valid_emails(db: Session) -> List[Attendee]:
    """
    Get a list of unique attendees who have email addresses.

    Args:
        db: Database session

    Returns:
        List[Attendee]: List of attendee objects with email addresses
    """
    # Get all attendees with valid email addresses
    attendees = db.query(Attendee).filter(Attendee.email.isnot(None)).all()
    return attendees


def get_attendee_stats(db: Session, attendee_id: int) -> Dict[str, Any]:
    """
    Get statistics for a specific attendee.

    Args:
        db: Database session
        attendee_id: Attendee ID

    Returns:
        Dict[str, Any]: Dictionary with attendee statistics
    """
    attendee = db.query(Attendee).filter(Attendee.id == attendee_id).first()
    if not attendee:
        return {}

    meetings_count = len(attendee.meetings)

    # Get total meeting duration for this attendee
    total_duration = sum(meeting.duration or 0 for meeting in attendee.meetings)

    # Get all unique co-attendees
    co_attendees = set()
    for meeting in attendee.meetings:
        for co_attendee in meeting.attendees:
            if co_attendee.id != attendee_id:
                co_attendees.add(co_attendee.id)

    return {
        "name": attendee.name,
        "email": attendee.email,
        "meetings_count": meetings_count,
        "total_duration_hours": (
            round(total_duration / 3600, 2) if total_duration else 0
        ),
        "unique_co_attendees": len(co_attendees),
    }


def format_timestamp(seconds: float) -> str:
    """
    Format seconds as MM:SS for transcript timestamps.

    Args:
        seconds: Time in seconds

    Returns:
        String in MM:SS format
    """
    if seconds is None:
        return "00:00"

    minutes, secs = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def update_denormalized_meeting_view(db: Session, meeting_id: int) -> None:
    """
    Update the denormalized meeting view for a given meeting.
    This pre-computes all the data needed for YAML export.

    Args:
        db: Database session
        meeting_id: Meeting ID
    """
    # Get the meeting and all related data
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        return

    # Prepare the denormalized data
    attendees_data = [
        {"id": attendee.id, "name": attendee.name, "email": attendee.email}
        for attendee in meeting.attendees
    ]

    action_items_data = [
        {
            "id": item.id,
            "title": item.title,
            "description": item.description,
            "status": item.status,
            "assignee_name": item.assignee_name,
            "assignee_email": item.assignee_email,
        }
        for item in meeting.action_items
    ]

    # Sort transcript entries by timestamp
    transcript_entries = sorted(meeting.transcript_entries, key=lambda x: x.timestamp)
    transcript_data = [
        {
            "id": entry.id,
            "speaker": entry.speaker,
            "text": entry.text,
            "timestamp": entry.timestamp,
            "formatted_time": format_timestamp(entry.timestamp),
        }
        for entry in transcript_entries
    ]

    # Check if a denormalized view already exists
    denorm_view = (
        db.query(DenormalizedMeetingView)
        .filter(DenormalizedMeetingView.id == meeting_id)
        .first()
    )

    if denorm_view:
        # Update existing view
        denorm_view.name = meeting.name
        denorm_view.created_at = meeting.created_at
        denorm_view.duration = meeting.duration
        denorm_view.url = meeting.url
        denorm_view.recording_url = meeting.recording_url
        denorm_view.notes = meeting.notes
        denorm_view.external_id = meeting.external_id
        denorm_view.received_at = meeting.received_at
        denorm_view.attendees_data = attendees_data
        denorm_view.action_items_data = action_items_data
        denorm_view.transcript_data = transcript_data
        denorm_view.last_updated = datetime.now()
    else:
        # Create new view
        denorm_view = DenormalizedMeetingView(
            id=meeting.id,
            name=meeting.name,
            created_at=meeting.created_at,
            duration=meeting.duration,
            url=meeting.url,
            recording_url=meeting.recording_url,
            notes=meeting.notes,
            external_id=meeting.external_id,
            received_at=meeting.received_at,
            attendees_data=attendees_data,
            action_items_data=action_items_data,
            transcript_data=transcript_data,
            last_updated=datetime.now(),
        )
        db.add(denorm_view)

    # Commit changes
    db.commit()


def get_denormalized_meeting(
    db: Session, meeting_id: int
) -> Optional[DenormalizedMeeting]:
    """
    Get the denormalized meeting data for a given meeting as a Pydantic model.
    If the denormalized view doesn't exist, it creates it.

    Args:
        db: Database session
        meeting_id: Meeting ID

    Returns:
        DenormalizedMeeting: Pydantic model with denormalized meeting data
    """
    # Try to get from denormalized view
    denorm_view = (
        db.query(DenormalizedMeetingView)
        .filter(DenormalizedMeetingView.id == meeting_id)
        .first()
    )

    if not denorm_view:
        # Create the denormalized view
        update_denormalized_meeting_view(db, meeting_id)

        # Try again
        denorm_view = (
            db.query(DenormalizedMeetingView)
            .filter(DenormalizedMeetingView.id == meeting_id)
            .first()
        )

        if not denorm_view:
            # Meeting doesn't exist
            return None

    # Convert to Pydantic model for type checking and better data handling
    attendees = [
        DenormalizedAttendee(**attendee) for attendee in denorm_view.attendees_data
    ]

    action_items = [
        DenormalizedActionItem(**item) for item in denorm_view.action_items_data
    ]

    transcript = [
        DenormalizedTranscriptEntry(**entry) for entry in denorm_view.transcript_data
    ]

    # Create and return the full DenormalizedMeeting model
    return DenormalizedMeeting(
        id=denorm_view.id,
        name=denorm_view.name,
        created_at=denorm_view.created_at,
        duration=denorm_view.duration,
        url=denorm_view.url,
        recording_url=denorm_view.recording_url,
        notes=denorm_view.notes,
        external_id=denorm_view.external_id,
        received_at=denorm_view.received_at,
        attendees=attendees,
        action_items=action_items,
        transcript=transcript,
        last_updated=denorm_view.last_updated,
    )


def get_analytics_data(
    db: Session, time_period: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get analytics data for all meetings, optionally filtered by time period.

    Args:
        db: Database session
        time_period: Optional time filter (week, month, year)

    Returns:
        Dict with various analytics metrics
    """
    # Set up time filter if specified
    date_filter = None
    if time_period:
        now = datetime.now()
        if time_period == "week":
            date_filter = now - timedelta(days=7)
        elif time_period == "month":
            date_filter = now - timedelta(days=30)
        elif time_period == "year":
            date_filter = now - timedelta(days=365)

    # Base query for meetings
    meetings_query = db.query(Meeting)
    if date_filter:
        meetings_query = meetings_query.filter(Meeting.created_at >= date_filter)

    # Get all meetings in the time period
    meetings = meetings_query.all()

    # Basic meeting metrics
    total_meetings = len(meetings)
    total_duration = sum(meeting.duration or 0 for meeting in meetings)
    avg_duration = total_duration / total_meetings if total_meetings > 0 else 0

    # Get meeting counts by month
    meetings_by_month = {}
    for meeting in meetings:
        month_key = meeting.created_at.strftime("%Y-%m")
        if month_key in meetings_by_month:
            meetings_by_month[month_key] += 1
        else:
            meetings_by_month[month_key] = 1

    # Ensure at least one entry
    if not meetings_by_month:
        meetings_by_month = {"2025-03": 0}

    # Get transcript word counts for each meeting
    meeting_word_counts = []
    for meeting in meetings:
        try:
            # Get denormalized meeting data for transcript analysis
            denorm_meeting = get_denormalized_meeting(db, meeting.id)
            if denorm_meeting and denorm_meeting.transcript:
                # Calculate word count
                word_count = denorm_meeting.transcript_word_count()

                # Get word counts by speaker
                speaker_word_counts = {}
                for entry in denorm_meeting.transcript:
                    speaker = entry.speaker
                    words = len(entry.text.split())

                    if speaker in speaker_word_counts:
                        speaker_word_counts[speaker] += words
                    else:
                        speaker_word_counts[speaker] = words

                meeting_word_counts.append(
                    {
                        "meeting_id": meeting.id,
                        "meeting_name": meeting.name,
                        "created_at": meeting.created_at,
                        "total_words": word_count,
                        "speaker_word_counts": speaker_word_counts,
                    }
                )
        except Exception as e:
            # Log error but continue processing other meetings
            print(f"Error processing meeting {meeting.id}: {str(e)}")

    # Sort meetings by word count
    meeting_word_counts.sort(key=lambda x: x["total_words"], reverse=True)

    # Top speakers across all meetings
    all_speakers = {}
    for meeting_data in meeting_word_counts:
        for speaker, count in meeting_data["speaker_word_counts"].items():
            if speaker in all_speakers:
                all_speakers[speaker]["total_words"] += count
                all_speakers[speaker]["meeting_count"] += 1
            else:
                all_speakers[speaker] = {"total_words": count, "meeting_count": 1}

    # Convert to list and sort by total words
    top_speakers = [{"name": speaker, **data} for speaker, data in all_speakers.items()]
    top_speakers.sort(key=lambda x: x["total_words"], reverse=True)

    # Ensure we have at least an empty list if no speakers found
    if not top_speakers:
        top_speakers = []

    # Get action item statistics
    action_items_query = db.query(ActionItem)
    if date_filter:
        # Join to meeting to apply the date filter
        action_items_query = action_items_query.join(Meeting).filter(
            Meeting.created_at >= date_filter
        )

    action_items = action_items_query.all()
    action_item_counts = {
        "total": len(action_items),
        "completed": len([item for item in action_items if item.status == "completed"]),
        "pending": len([item for item in action_items if item.status == "pending"]),
        "in_progress": len(
            [item for item in action_items if item.status == "in_progress"]
        ),
    }

    # Return the compiled analytics data
    return {
        "total_meetings": total_meetings,
        "total_duration_hours": round(total_duration / 3600, 1),
        "avg_duration_minutes": round(avg_duration / 60, 1),
        "meetings_by_month": dict(sorted(meetings_by_month.items())),
        "meeting_word_counts": meeting_word_counts[
            :10
        ],  # Top 10 meetings by word count
        "top_speakers": top_speakers[:10],  # Top 10 speakers by word count
        "action_items": action_item_counts,
    }


def get_user_analytics(db: Session, email: str) -> Dict[str, Any]:
    """
    Get analytics data for a specific user by email.

    Args:
        db: Database session
        email: User's email address

    Returns:
        Dict with user-specific analytics metrics
    """
    # Find the attendee by email
    attendee = db.query(Attendee).filter(Attendee.email == email).first()
    if not attendee:
        return {"error": "User not found"}

    # Get all meetings this user attended
    meetings = attendee.meetings
    total_meetings = len(meetings)

    # Calculate total time spent in meetings
    total_duration = sum(meeting.duration or 0 for meeting in meetings)

    # Get word counts for this user across all meetings
    user_word_counts = []
    user_total_words = 0
    meetings_with_transcript = 0

    for meeting in meetings:
        denorm_meeting = get_denormalized_meeting(db, meeting.id)
        if denorm_meeting and denorm_meeting.transcript:
            meetings_with_transcript += 1
            user_words = 0

            # Count words spoken by this user
            for entry in denorm_meeting.transcript:
                if entry.speaker.lower() == attendee.name.lower():
                    user_words += len(entry.text.split())

            user_total_words += user_words

            # Add to meeting-specific data
            user_word_counts.append(
                {
                    "meeting_id": meeting.id,
                    "meeting_name": meeting.name,
                    "created_at": meeting.created_at,
                    "words_spoken": user_words,
                    "meeting_total_words": denorm_meeting.transcript_word_count(),
                }
            )

    # Sort by words spoken
    user_word_counts.sort(key=lambda x: x["words_spoken"], reverse=True)

    # Get action items assigned to this user
    action_items = db.query(ActionItem).filter(ActionItem.assignee_email == email).all()

    action_item_stats = {
        "total": len(action_items),
        "completed": len([item for item in action_items if item.status == "completed"]),
        "pending": len([item for item in action_items if item.status == "pending"]),
        "in_progress": len(
            [item for item in action_items if item.status == "in_progress"]
        ),
    }

    # Calculate average words per meeting (only for meetings with transcripts)
    avg_words_per_meeting = (
        user_total_words / meetings_with_transcript
        if meetings_with_transcript > 0
        else 0
    )

    # Get co-attendees
    co_attendees = set()
    for meeting in meetings:
        for co_attendee in meeting.attendees:
            if co_attendee.id != attendee.id and co_attendee.email:
                co_attendees.add((co_attendee.id, co_attendee.name, co_attendee.email))

    # Return the compiled user analytics
    return {
        "user": {
            "name": attendee.name,
            "email": attendee.email,
        },
        "meeting_stats": {
            "total_meetings": total_meetings,
            "total_duration_hours": round(total_duration / 3600, 1),
            "avg_duration_minutes": (
                round((total_duration / total_meetings) / 60, 1)
                if total_meetings > 0
                else 0
            ),
        },
        "speech_stats": {
            "total_words": user_total_words,
            "avg_words_per_meeting": round(avg_words_per_meeting, 0),
            "meetings_with_transcript": meetings_with_transcript,
            "meeting_word_counts": user_word_counts[
                :10
            ],  # Top 10 meetings by word count
        },
        "action_items": action_item_stats,
        "network": {"unique_co_attendees": len(co_attendees)},
    }
