"""
Tests for meeting service functions.
"""
import pytest
from datetime import datetime

from app.services import meeting_service
from app.schemas.meeting import WebhookPayload, DenormalizedMeeting


def test_create_meeting_from_webhook(db_session, sample_meeting_data):
    """Test creating a meeting from webhook payload."""
    # Create payload
    payload = WebhookPayload(**sample_meeting_data)
    
    # Create meeting
    meeting = meeting_service.create_meeting_from_webhook(db_session, payload)
    
    # Verify meeting data
    assert meeting.name == payload.name
    assert meeting.external_id == payload.id
    assert meeting.duration == payload.duration
    assert meeting.url == payload.url
    assert meeting.recording_url == payload.recordingUrl
    
    # Verify attendees
    assert len(meeting.attendees) == 2
    attendee_emails = [a.email for a in meeting.attendees]
    assert "john@example.com" in attendee_emails
    assert "jane@example.com" in attendee_emails
    
    # Verify action items
    assert len(meeting.action_items) == 1
    assert meeting.action_items[0].title == "Research new feature"
    
    # Verify transcript
    assert len(meeting.transcript_entries) == 2
    assert meeting.transcript_entries[0].speaker == "John Doe"
    assert meeting.transcript_entries[1].speaker == "Jane Smith"


def test_get_meeting(db_session, db_meeting):
    """Test retrieving a meeting by ID."""
    # Get meeting
    meeting = meeting_service.get_meeting(db_session, db_meeting.id)
    
    # Verify meeting exists and matches
    assert meeting is not None
    assert meeting.id == db_meeting.id
    assert meeting.name == db_meeting.name


def test_get_meeting_not_found(db_session):
    """Test retrieving a non-existent meeting."""
    # Get non-existent meeting
    meeting = meeting_service.get_meeting(db_session, 999)
    
    # Verify meeting is None
    assert meeting is None


def test_get_meetings(db_session, db_meeting):
    """Test retrieving a list of meetings."""
    # Get list of meetings
    meetings = meeting_service.get_meetings(db_session)
    
    # Verify list has at least one meeting
    assert len(meetings) >= 1
    
    # Find our test meeting in the list
    found = False
    for meeting in meetings:
        if meeting.id == db_meeting.id:
            found = True
            break
    
    assert found, "Test meeting not found in meeting list"


def test_denormalized_meeting_view(db_session, db_meeting):
    """Test denormalized meeting view functions."""
    # Create denormalized view
    meeting_service.update_denormalized_meeting_view(db_session, db_meeting.id)
    
    # Get denormalized meeting
    denorm_meeting = meeting_service.get_denormalized_meeting(db_session, db_meeting.id)
    
    # Verify denormalized meeting data
    assert denorm_meeting is not None
    assert isinstance(denorm_meeting, DenormalizedMeeting)
    assert denorm_meeting.id == db_meeting.id
    assert denorm_meeting.name == db_meeting.name
    
    # Check lists
    assert len(denorm_meeting.attendees) == 2
    assert len(denorm_meeting.action_items) == 1
    assert len(denorm_meeting.transcript) == 2
    
    # Test helper methods
    assert denorm_meeting.duration_minutes() == 60.0
    assert denorm_meeting.attendee_count() == 2
    assert denorm_meeting.transcript_length() == 2
    assert denorm_meeting.transcript_word_count() > 0
    assert denorm_meeting.has_recording() == True
    
    # Test YAML formatting
    yaml_dict = denorm_meeting.simplified_for_yaml
    assert yaml_dict["title"] == db_meeting.name
    assert "attendees" in yaml_dict
    assert "transcript" in yaml_dict
    assert "action_items" in yaml_dict