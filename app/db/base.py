"""
Import all models here to ensure they are registered with SQLAlchemy.
"""

from app.db.base_class import Base  # noqa
from app.models.meeting import Meeting, Attendee, ActionItem, TranscriptEntry  # noqa
