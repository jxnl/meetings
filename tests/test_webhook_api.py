"""
Tests for webhook API endpoints.
"""

from fastapi import status

from app.services import meeting_service


def test_create_meeting_webhook(client, sample_meeting_data, monkeypatch):
    """Test creating a meeting via webhook."""
    # Mock the update_denormalized_meeting_view function instead of BackgroundTasks
    original_function = meeting_service.update_denormalized_meeting_view
    called = []

    def mock_update(*args, **kwargs):
        called.append(True)
        return original_function(*args, **kwargs)

    monkeypatch.setattr(
        "app.services.meeting_service.update_denormalized_meeting_view", mock_update
    )

    # Generate unique external_id to avoid conflicts
    import random

    sample_meeting_data["id"] = random.randint(10000, 99999)

    # Send webhook payload
    response = client.post("/api/webhooks/", json=sample_meeting_data)

    # Verify response
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == sample_meeting_data["name"]
    assert data["external_id"] == sample_meeting_data["id"]


def test_get_meeting(client, db_meeting):
    """Test retrieving a meeting by ID."""
    response = client.get(f"/api/webhooks/{db_meeting.id}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == db_meeting.id
    assert data["name"] == db_meeting.name
    assert len(data["attendees"]) == 2
    assert len(data["action_items"]) == 1
    assert len(data["transcript_entries"]) == 2


def test_get_meeting_not_found(client):
    """Test retrieving a non-existent meeting."""
    response = client.get("/api/webhooks/999")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"]


def test_list_meetings(client, db_meeting):
    """Test listing all meetings."""
    response = client.get("/api/webhooks/")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)

    # Meeting might be in any position in the list
    ids = [meeting["id"] for meeting in data]
    assert db_meeting.id in ids


def test_delete_meeting(client, db_meeting, db_session):
    """Test deleting a meeting."""
    # Get the meeting ID
    meeting_id = db_meeting.id

    # Delete the meeting
    response = client.delete(f"/api/webhooks/{meeting_id}")

    # Verify successful deletion
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify meeting is deleted by trying to get it
    get_response = client.get(f"/api/webhooks/{meeting_id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND
