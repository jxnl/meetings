"""
Pydantic schemas for meeting data validation and serialization.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, EmailStr


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
