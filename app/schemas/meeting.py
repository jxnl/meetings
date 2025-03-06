"""
Pydantic schemas for meeting data validation and serialization.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field, EmailStr, root_validator


class AttendeeBase(BaseModel):
    """Base schema for attendee data."""

    name: str
    email: Optional[str] = None


class AttendeeCreate(AttendeeBase):
    """Schema for creating an attendee."""

    pass


class Attendee(AttendeeBase):
    """Schema for attendee response."""

    id: int

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class ActionItemBase(BaseModel):
    """Base schema for action item data."""

    title: str
    description: Optional[str] = None
    status: str = "PENDING"
    assignee_name: Optional[str] = None
    assignee_email: Optional[str] = None
    external_id: Optional[int] = None


class ActionItemCreate(ActionItemBase):
    """Schema for creating an action item."""

    pass


class ActionItem(ActionItemBase):
    """Schema for action item response."""

    id: int
    meeting_id: int

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class TranscriptEntryBase(BaseModel):
    """Base schema for transcript entry data."""

    speaker: str
    text: str
    timestamp: float


class TranscriptEntryCreate(TranscriptEntryBase):
    """Schema for creating a transcript entry."""

    pass


class TranscriptEntry(TranscriptEntryBase):
    """Schema for transcript entry response."""

    id: int
    meeting_id: int

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class MeetingBase(BaseModel):
    """Base schema for meeting data."""

    name: str
    created_at: datetime
    duration: Optional[float] = None
    url: Optional[str] = None
    recording_url: Optional[str] = None
    notes: Optional[str] = None
    external_id: Optional[int] = None


class MeetingCreate(MeetingBase):
    """Schema for creating a meeting."""

    attendees: Optional[List[AttendeeCreate]] = []
    action_items: Optional[List[ActionItemCreate]] = []
    transcript_entries: Optional[List[TranscriptEntryCreate]] = []


class Meeting(MeetingBase):
    """Schema for meeting response."""

    id: int
    received_at: datetime
    attendees: List[Attendee] = []
    action_items: List[ActionItem] = []
    transcript_entries: List[TranscriptEntry] = []

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class WebhookPayload(BaseModel):
    """Schema for incoming webhook payload."""

    id: int = Field(..., description="Meeting ID from the source system")
    name: str = Field(..., description="Meeting name")
    createdAt: datetime = Field(..., description="When the meeting was created")
    duration: Optional[float] = Field(
        None, description="Duration of the meeting in seconds"
    )
    url: Optional[str] = Field(None, description="URL of the meeting")
    attendees: List[AttendeeCreate] = Field([], description="List of meeting attendees")
    recordingUrl: Optional[str] = Field(None, description="URL of the recording")
    notes: Optional[str] = Field(None, description="Meeting notes in markdown format")
    actionItems: Optional[List[ActionItemCreate]] = Field(
        [], description="List of action items"
    )
    transcript: Optional[List[TranscriptEntryCreate]] = Field(
        [], description="List of transcript entries"
    )


# Denormalized View Schemas


class DenormalizedAttendee(BaseModel):
    """Schema for denormalized attendee data."""

    id: int
    name: str
    email: Optional[str] = None


class DenormalizedTranscriptEntry(BaseModel):
    """Schema for denormalized transcript entry data with pre-formatted time."""

    id: int
    speaker: str
    text: str
    timestamp: float
    formatted_time: str  # Pre-formatted time string (MM:SS or HH:MM:SS)


class DenormalizedActionItem(BaseModel):
    """Schema for denormalized action item data."""

    id: int
    title: str
    description: Optional[str] = None
    status: str = "PENDING"
    assignee_name: Optional[str] = None
    assignee_email: Optional[str] = None


class DenormalizedMeeting(BaseModel):
    """
    Schema for denormalized meeting data.
    This represents the pre-computed data structure for efficient YAML export.
    """

    id: int
    name: str
    created_at: datetime
    duration: Optional[float] = None
    url: Optional[str] = None
    recording_url: Optional[str] = None
    notes: Optional[str] = None
    external_id: Optional[int] = None
    received_at: datetime
    attendees: List[DenormalizedAttendee] = []
    action_items: List[DenormalizedActionItem] = []
    transcript: List[DenormalizedTranscriptEntry] = []
    last_updated: datetime

    # Convenience methods for common operations

    def duration_minutes(self) -> float:
        """Calculate meeting duration in minutes."""
        return round((self.duration or 0) / 60, 1)

    def attendee_count(self) -> int:
        """Get number of attendees."""
        return len(self.attendees)

    def transcript_length(self) -> int:
        """Get number of transcript entries."""
        return len(self.transcript)

    def transcript_word_count(self) -> int:
        """Calculate total number of words in transcript."""
        return sum(len(entry.text.split()) for entry in self.transcript)

    def has_recording(self) -> bool:
        """Check if meeting has a recording."""
        return self.recording_url is not None and len(self.recording_url) > 0

    # Derived properties

    @property
    def formatted_date(self) -> str:
        """Format the meeting date in a human-readable format."""
        return self.created_at.strftime("%Y-%m-%d %H:%M")

    @property
    def simplified_for_yaml(self) -> Dict[str, Any]:
        """Generate a simplified dictionary suitable for YAML export."""
        result = {
            "title": self.name,
            "date": self.formatted_date,
            "duration_minutes": self.duration_minutes(),
        }

        if self.recording_url:
            result["recording_url"] = self.recording_url

        if self.notes:
            result["notes"] = self.notes

        # Format attendees
        result["attendees"] = [
            {"name": a.name, **({"email": a.email} if a.email else {})}
            for a in self.attendees
        ]

        # Format action items
        if self.action_items:
            result["action_items"] = [
                {
                    "title": item.title,
                    **({"description": item.description} if item.description else {}),
                    **({"status": item.status} if item.status != "PENDING" else {}),
                    **({"assignee": item.assignee_name} if item.assignee_name else {}),
                }
                for item in self.action_items
            ]

        # Format transcript
        if self.transcript:
            result["transcript"] = [
                {
                    "speaker": entry.speaker,
                    "text": entry.text,
                    "time": entry.formatted_time,
                }
                for entry in self.transcript
            ]

        return result
