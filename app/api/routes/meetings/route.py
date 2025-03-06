"""
Routes for meeting management and display.
"""

from typing import List, Dict, Any
import yaml
from collections import defaultdict
from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, Request, Form, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.meeting import Meeting, Attendee, DenormalizedMeetingView
from app.services.meeting_service import (
    get_meetings,
    get_meeting,
    get_attendees,
    get_analytics_data,
    get_user_analytics,
    get_attendees_with_valid_emails,
    update_action_item_status,
)
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
    "gmail.com",
    "hotmail.com",
    "yahoo.com",
    "outlook.com",
    "aol.com",
    "icloud.com",
    "mail.com",
    "protonmail.com",
    "zoho.com",
    "me.com",
    "msn.com",
    "live.com",
    "googlemail.com",
    "ymail.com",
    "example.com",
}


@router.get("/", response_class=HTMLResponse)
async def list_meetings(
    request: Request,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    domain: str = None,
    email: str = None,
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
            meeting
            for meeting in all_meetings
            if any(attendee.email == email for attendee in meeting.attendees)
        ]
        filter_description = f"Attendee: {email}"
    elif domain:
        # Filter meetings by attendee domain
        filtered_meetings = [
            meeting
            for meeting in all_meetings
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
        "meetings/list.html",
        {
            "request": request,
            "meetings": filtered_meetings,
            "filter_description": filter_description,
            "total_meetings": len(all_meetings),
            "filtered_count": len(filtered_meetings),
        },
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
        email_parts = attendee.email.split("@")
        if len(email_parts) != 2:
            continue

        domain = email_parts[1].lower()

        # Skip generic domains but include our demo domains
        if domain in GENERIC_DOMAINS:
            continue

        # Add attendee to domain group
        domains[domain].append(
            {
                "id": attendee.id,
                "name": attendee.name,
                "email": attendee.email,
                "meetings_count": len(attendee.meetings),
            }
        )

    # Convert to list for sorting
    domain_list = []
    for domain, attendees_list in domains.items():
        domain_list.append(
            {
                "domain": domain,
                "attendees": sorted(attendees_list, key=lambda x: x["name"]),
                "attendee_count": len(attendees_list),
            }
        )

    # Sort domains by count (descending)
    domain_list.sort(key=lambda x: x["attendee_count"], reverse=True)

    return templates.TemplateResponse(
        "meetings/domains.html",
        {
            "request": request,
            "domains": domain_list,
            "total_domains": len(domain_list),
            "total_company_attendees": sum(len(d["attendees"]) for d in domain_list),
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
        # Use the denormalized view with Pydantic models for better type safety and readability
        from app.services.meeting_service import get_denormalized_meeting

        # Get denormalized meeting data (creates it if it doesn't exist)
        meeting = get_denormalized_meeting(db, meeting_id)
        if not meeting:
            continue

        # Use the built-in helper method to create the YAML-friendly dictionary
        # This encapsulates all the formatting logic in the Pydantic model
        simplified_meeting = meeting.simplified_for_yaml

        # Add to the result
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


@router.get("/analytics", response_class=HTMLResponse)
async def meeting_analytics(
    request: Request,
    db: Session = Depends(get_db),
    time_period: str = None,
    email: str = None,
):
    """
    Display analytics dashboard for meetings data.

    Args:
        request: FastAPI request object
        db: Database session
        time_period: Optional time period to filter by (week, month, year)
        email: Optional user email to get user-specific analytics

    Returns:
        HTMLResponse: Rendered analytics template
    """
    # If email is provided, show user-specific analytics
    if email:
        analytics_data = get_user_analytics(db, email)
        template_name = "meetings/user_analytics.html"
    else:
        # Otherwise show general analytics
        analytics_data = get_analytics_data(db, time_period)
        template_name = "meetings/analytics.html"

    # Get list of attendees with emails for user selection dropdown
    attendees = get_attendees_with_valid_emails(db)

    return templates.TemplateResponse(
        template_name,
        {
            "request": request,
            "analytics": analytics_data,
            "attendees": attendees,
            "time_period": time_period or "all time",
            "email": email,
        },
    )


@router.get("/organizations", response_class=HTMLResponse)
async def list_organizations(request: Request, db: Session = Depends(get_db)):
    """
    List organizations based on email domains with their action items and notes.
    Generic domains like gmail.com are treated as individual users.

    Args:
        request: FastAPI request object
        db: Database session

    Returns:
        HTMLResponse: Rendered template with organizations and their data
    """
    attendees = get_attendees_with_valid_emails(db)
    
    # Group attendees by domain with special handling for generic domains
    organizations = defaultdict(list)
    
    for attendee in attendees:
        if not attendee.email:
            continue
            
        # Extract domain from email
        email_parts = attendee.email.split("@")
        if len(email_parts) != 2:
            continue
            
        domain = email_parts[1].lower()
        
        # For generic domains, use the full email as the "domain"
        if domain in GENERIC_DOMAINS:
            domain_key = attendee.email.lower()  # Treat each person as their own "organization"
        else:
            domain_key = domain
            
        # Add attendee to organization group
        organizations[domain_key].append({
            "id": attendee.id,
            "name": attendee.name,
            "email": attendee.email,
            "is_generic": domain in GENERIC_DOMAINS,
        })
    
    # Process each organization
    org_data = []
    
    for domain, members in organizations.items():
        # Find all unfinished action items for this organization
        action_items = []
        meeting_notes = []
        meeting_ids = set()
        
        for member in members:
            attendee = db.query(Attendee).filter(Attendee.id == member["id"]).first()
            if not attendee:
                continue
                
            # Get all meetings for this attendee
            for meeting in attendee.meetings:
                meeting_ids.add(meeting.id)
        
        # Get unfinished action items for all meetings in this organization
        for meeting_id in meeting_ids:
            meeting = get_meeting(db, meeting_id)
            if not meeting:
                continue
                
            # Get unfinished action items
            for item in meeting.action_items:
                if item.status.upper() != "COMPLETED":
                    action_items.append({
                        "id": item.id,
                        "title": item.title,
                        "description": item.description,
                        "status": item.status,
                        "assignee_name": item.assignee_name,
                        "assignee_email": item.assignee_email,
                        "meeting_id": meeting_id,
                        "meeting_name": meeting.name,
                    })
            
            # Add meeting notes if they exist
            if meeting.notes:
                meeting_notes.append({
                    "meeting_id": meeting.id,
                    "meeting_name": meeting.name,
                    "created_at": meeting.created_at,
                    "notes": meeting.notes,
                })
        
        # Add to the organization data
        org_data.append({
            "domain": domain,
            "display_name": domain if not members[0]["is_generic"] else members[0]["name"],
            "is_generic": members[0]["is_generic"],
            "members": sorted(members, key=lambda x: x["name"]),
            "member_count": len(members),
            "action_items": sorted(action_items, key=lambda x: x["status"]),
            "action_items_count": len(action_items),
            "meeting_notes": sorted(meeting_notes, key=lambda x: x["created_at"], reverse=True),
            "meeting_ids": list(meeting_ids),
        })
    
    # Sort organizations by member count (descending)
    org_data.sort(key=lambda x: x["member_count"], reverse=True)
    
    return templates.TemplateResponse(
        "meetings/organizations.html",
        {
            "request": request,
            "organizations": org_data,
            "total_organizations": len(org_data),
            "total_action_items": sum(org["action_items_count"] for org in org_data),
        },
    )


@router.post("/action-items/{action_item_id}/update", response_class=JSONResponse)
async def update_action_item(
    action_item_id: int, 
    status: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Update the status of an action item.
    
    Args:
        action_item_id: ID of the action item to update
        status: New status for the action item
        db: Database session
        
    Returns:
        JSONResponse: Status of the update operation
    """
    success = update_action_item_status(db, action_item_id, status.upper())
    
    if not success:
        return JSONResponse(
            status_code=404,
            content={"success": False, "message": "Action item not found"}
        )
        
    return JSONResponse(
        content={"success": True, "message": "Action item updated successfully"}
    )
