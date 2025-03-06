"""
API routes for handling webhook requests.
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.meeting import WebhookPayload, Meeting
from app.services import meeting_service

router = APIRouter()


@router.post("/", response_model=Meeting, status_code=status.HTTP_201_CREATED)
async def receive_webhook(
    payload: WebhookPayload,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Receive a webhook payload and process it.

    Args:
        payload: The webhook payload
        background_tasks: FastAPI background tasks
        db: Database session

    Returns:
        Meeting: The created meeting
    """
    # Check if meeting with this external ID already exists
    existing_meeting = meeting_service.get_meeting_by_external_id(db, payload.id)
    if existing_meeting:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Meeting with external ID {payload.id} already exists",
        )

    # Process the webhook payload
    try:
        meeting = meeting_service.create_meeting_from_webhook(db, payload)
        return meeting
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process webhook: {str(e)}",
        )


@router.get("/{meeting_id}", response_model=Meeting)
async def get_meeting(meeting_id: int, db: Session = Depends(get_db)):
    """
    Get a meeting by ID.

    Args:
        meeting_id: Meeting ID
        db: Database session

    Returns:
        Meeting: The meeting
    """
    meeting = meeting_service.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meeting with ID {meeting_id} not found",
        )
    return meeting


@router.get("/", response_model=list[Meeting])
async def get_meetings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get a list of meetings.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session

    Returns:
        List[Meeting]: List of meetings
    """
    meetings = meeting_service.get_meetings(db, skip=skip, limit=limit)
    return meetings


@router.delete("/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meeting(meeting_id: int, db: Session = Depends(get_db)):
    """
    Delete a meeting by ID.

    Args:
        meeting_id: Meeting ID
        db: Database session

    Returns:
        None
    """
    deleted = meeting_service.delete_meeting(db, meeting_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meeting with ID {meeting_id} not found",
        )
    return None
