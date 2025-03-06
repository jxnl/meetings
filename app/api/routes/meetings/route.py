"""
Routes for meeting management and display.
"""

from typing import List, Dict, Any
import yaml
from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.meeting import Meeting
from app.services.meeting_service import get_meetings, get_meeting
from app.schemas.meeting import Meeting as MeetingSchema

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def list_meetings(
    request: Request, db: Session = Depends(get_db), skip: int = 0, limit: int = 100
):
    """
    Display a list of all meetings with checkboxes for selection.

    Args:
        request: FastAPI request object
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        HTMLResponse: Rendered meetings list template
    """
    meetings = get_meetings(db, skip=skip, limit=limit)
    return templates.TemplateResponse(
        "meetings/list.html", {"request": request, "meetings": meetings}
    )


@router.post("/generate-yaml", response_class=HTMLResponse)
async def generate_yaml(
    request: Request, meeting_ids: List[int] = Form(...), db: Session = Depends(get_db)
):
    """
    Generate YAML representation of selected meetings.

    Args:
        request: FastAPI request object
        meeting_ids: List of selected meeting IDs
        db: Database session

    Returns:
        HTMLResponse: Rendered template with YAML representation
    """
    meetings_data = []

    for meeting_id in meeting_ids:
        meeting = get_meeting(db, meeting_id)
        if not meeting:
            continue

        # Convert to Pydantic model for easier serialization
        meeting_schema = MeetingSchema.model_validate(meeting)

        # Convert to dict and prepare for YAML
        meeting_dict = meeting_schema.model_dump()

        # Ensure attendees are properly formatted and prioritized
        simplified_meeting = {
            "title": meeting_dict["name"],
            "date": meeting_dict["created_at"].strftime("%Y-%m-%d %H:%M"),
        }

        # Format attendees for better readability in YAML
        if meeting_dict.get("attendees"):
            attendees_formatted = []
            for attendee in meeting_dict["attendees"]:
                attendee_info = {"name": attendee["name"]}
                if attendee.get("email"):
                    attendee_info["email"] = attendee["email"]
                attendees_formatted.append(attendee_info)

            simplified_meeting["attendees"] = attendees_formatted
        else:
            simplified_meeting["attendees"] = []

        meetings_data.append(simplified_meeting)

    # Generate YAML with better formatting
    yaml_content = yaml.dump(
        meetings_data,
        sort_keys=False,
        default_flow_style=False,
        width=120,  # Wider output for better readability
        indent=2,  # Consistent indentation
    )

    return templates.TemplateResponse(
        "meetings/yaml_result.html",
        {
            "request": request,
            "yaml_content": yaml_content,
            "meetings_count": len(meetings_data),
        },
    )
