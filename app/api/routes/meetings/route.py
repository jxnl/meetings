"""
Routes for meeting management and display.
"""

from typing import List, Dict, Any
import yaml
from collections import defaultdict
from datetime import timedelta
from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.meeting import Meeting, Attendee
from app.services.meeting_service import get_meetings, get_meeting, get_attendees
from app.schemas.meeting import Meeting as MeetingSchema


def time_format(seconds: float) -> str:
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

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# List of generic email domains to exclude
GENERIC_DOMAINS = {
    "gmail.com", "hotmail.com", "yahoo.com", "outlook.com", "aol.com", 
    "icloud.com", "mail.com", "protonmail.com", "zoho.com", "me.com",
    "msn.com", "live.com", "googlemail.com", "ymail.com", "example.com"
}

# Note: For our demo, we'll include the big tech companies that we would
# normally exclude in a real app to demonstrate the domain filtering
DEMO_INCLUDE = {
    "google.com", "microsoft.com", "apple.com", "amazon.com", "salesforce.com"
}


@router.get("/", response_class=HTMLResponse)
async def list_meetings(
    request: Request, 
    db: Session = Depends(get_db), 
    skip: int = 0, 
    limit: int = 100,
    domain: str = None,
    email: str = None
):
    """
    Display a list of all meetings with checkboxes for selection.
    Supports filtering by domain or email.

    Args:
        request: FastAPI request object
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        domain: Optional domain to filter by
        email: Optional email to filter by

    Returns:
        HTMLResponse: Rendered meetings list template
    """
    # Get all meetings first
    all_meetings = get_meetings(db, skip=skip, limit=limit)
    
    # Apply filters if specified
    if email:
        # Filter meetings by attendee email
        filtered_meetings = [
            meeting for meeting in all_meetings
            if any(attendee.email == email for attendee in meeting.attendees)
        ]
        filter_description = f"Attendee: {email}"
    elif domain:
        # Filter meetings by attendee domain
        filtered_meetings = [
            meeting for meeting in all_meetings
            if any(
                attendee.email and attendee.email.lower().endswith(f"@{domain.lower()}")
                for attendee in meeting.attendees
            )
        ]
        filter_description = f"Domain: {domain}"
    else:
        # No filter
        filtered_meetings = all_meetings
        filter_description = None
    
    return templates.TemplateResponse(
        "meetings/list.html", {
            "request": request, 
            "meetings": filtered_meetings,
            "filter_description": filter_description,
            "total_meetings": len(all_meetings),
            "filtered_count": len(filtered_meetings)
        }
    )


@router.get("/domains", response_class=HTMLResponse)
async def list_company_domains(request: Request, db: Session = Depends(get_db)):
    """
    List attendees by company domains (excluding generic email providers).

    Args:
        request: FastAPI request object
        db: Database session

    Returns:
        HTMLResponse: Rendered template with company domains and attendees
    """
    from app.services.meeting_service import get_attendees_with_valid_emails
    
    attendees = get_attendees_with_valid_emails(db)
    
    # Group attendees by domain
    domains = defaultdict(list)
    
    for attendee in attendees:
        if not attendee.email:
            continue
            
        # Extract domain from email
        email_parts = attendee.email.split('@')
        if len(email_parts) != 2:
            continue
            
        domain = email_parts[1].lower()
        
        # Skip generic domains but include our demo domains
        if domain in GENERIC_DOMAINS and domain not in DEMO_INCLUDE:
            continue
            
        # Add attendee to domain group
        domains[domain].append({
            'id': attendee.id,
            'name': attendee.name,
            'email': attendee.email,
            'meetings_count': len(attendee.meetings)
        })
    
    # Convert to list for sorting
    domain_list = []
    for domain, attendees_list in domains.items():
        domain_list.append({
            'domain': domain,
            'attendees': sorted(attendees_list, key=lambda x: x['name']),
            'attendee_count': len(attendees_list)
        })
    
    # Sort domains by count (descending)
    domain_list.sort(key=lambda x: x['attendee_count'], reverse=True)
    
    return templates.TemplateResponse(
        "meetings/domains.html",
        {
            "request": request,
            "domains": domain_list,
            "total_domains": len(domain_list),
            "total_company_attendees": sum(len(d['attendees']) for d in domain_list),
        },
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
        # Instead of using model_validate, create the dict manually to avoid validation issues
        # meeting_schema = MeetingSchema.model_validate(meeting)
        meeting_dict = {
            "id": meeting.id,
            "name": meeting.name,
            "created_at": meeting.created_at,
            "duration": meeting.duration,
            "url": meeting.url,
            "recording_url": meeting.recording_url,
            "notes": meeting.notes,
            "external_id": meeting.external_id,
            "received_at": meeting.received_at,
            "attendees": [
                {
                    "id": attendee.id,
                    "name": attendee.name,
                    "email": attendee.email
                } for attendee in meeting.attendees
            ],
            "action_items": [
                {
                    "id": item.id,
                    "title": item.title,
                    "description": item.description,
                    "status": item.status,
                    "assignee_name": item.assignee_name,
                    "assignee_email": item.assignee_email,
                    "external_id": item.external_id,
                    "meeting_id": item.meeting_id
                } for item in meeting.action_items
            ],
            "transcript_entries": [
                {
                    "id": entry.id,
                    "speaker": entry.speaker,
                    "text": entry.text,
                    "timestamp": entry.timestamp,
                    "meeting_id": entry.meeting_id
                } for entry in meeting.transcript_entries
            ]
        }

        # Process the meeting data from the database
        # We now have all data including transcript entries in the meeting_dict

        # Create structured meeting data for YAML
        simplified_meeting = {
            "title": meeting_dict["name"],
            "date": meeting_dict["created_at"].strftime("%Y-%m-%d %H:%M"),
            "duration_minutes": round((meeting_dict["duration"] or 0) / 60, 1),
        }
        
        # Add recording URL if available
        if meeting_dict.get("recording_url"):
            simplified_meeting["recording_url"] = meeting_dict["recording_url"]
            
        # Add notes if available
        if meeting_dict.get("notes"):
            simplified_meeting["notes"] = meeting_dict["notes"]

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
            
        # Add action items if available
        if meeting_dict.get("action_items") and len(meeting_dict["action_items"]) > 0:
            action_items_formatted = []
            for item in meeting_dict["action_items"]:
                action_item = {
                    "title": item["title"],
                }
                if item.get("description"):
                    action_item["description"] = item["description"]
                if item.get("status"):
                    action_item["status"] = item["status"]
                if item.get("assignee_name"):
                    action_item["assignee"] = item["assignee_name"]
                    
                action_items_formatted.append(action_item)
                
            simplified_meeting["action_items"] = action_items_formatted
            
        # Add transcript if available
        if meeting_dict.get("transcript_entries") and len(meeting_dict["transcript_entries"]) > 0:
            # Sort transcript entries by timestamp
            transcript_entries = sorted(
                meeting_dict["transcript_entries"], 
                key=lambda x: x["timestamp"]
            )
            
            transcript_formatted = []
            for entry in transcript_entries:
                transcript_item = {
                    "speaker": entry["speaker"],
                    "text": entry["text"],
                    "time": time_format(entry["timestamp"]),
                }
                transcript_formatted.append(transcript_item)
                
            simplified_meeting["transcript"] = transcript_formatted

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
