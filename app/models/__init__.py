"""
Models package initialization.
"""

from app.models.meeting import Meeting, Attendee, ActionItem, TranscriptEntry

# Add all models here for easy importing
__all__ = ["Meeting", "Attendee", "ActionItem", "TranscriptEntry"]
