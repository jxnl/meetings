from collections import defaultdict
from typing import List, Dict, Set

from app.core.logging import trace
from app.models.meeting import Attendee, Meeting
from app.services.meeting_service import (
    get_attendees_with_valid_emails,
    get_meeting_by_ids,
)

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


@trace(name="get_attendee_by_id")
def _get_attendee_by_id(db, attendee_id: int) -> Attendee:
    return db.query(Attendee).filter(Attendee.id == attendee_id).first()


@trace(name="get_attendee_by_ids")
def _get_attendee_by_ids(db, attendee_ids: List[int]) -> List[Attendee]:
    return db.query(Attendee).filter(Attendee.id.in_(attendee_ids)).all()


def get_organizations(db) -> List[dict]:
    organizations = defaultdict(list)
    all_meeting_ids: Set[int] = set()
    domain_meeting_ids: Dict[str, Set[int]] = defaultdict(set)

    # Fetch all attendees with valid emails (this already loads meetings relationship)
    attendees = get_attendees_with_valid_emails(db)

    # First pass: organize attendees by domain and collect all meeting IDs
    for attendee in attendees:
        if not attendee.email:
            continue

        email_parts = attendee.email.split("@")
        if len(email_parts) != 2:
            continue

        domain = email_parts[1].lower()
        domain_key = attendee.email.lower() if domain in GENERIC_DOMAINS else domain

        # Add attendee to appropriate organization
        organizations[domain_key].append(
            {
                "id": attendee.id,
                "name": attendee.name,
                "email": attendee.email,
                "is_generic": domain in GENERIC_DOMAINS,
            }
        )

        # Collect meeting IDs for this attendee
        attendee_meeting_ids = {meeting.id for meeting in attendee.meetings}
        domain_meeting_ids[domain_key].update(attendee_meeting_ids)
        all_meeting_ids.update(attendee_meeting_ids)

    # Single fetch for all meetings across all organizations
    all_meetings_by_id: Dict[int, Meeting] = {}
    if all_meeting_ids:
        meetings = get_meeting_by_ids(db, list(all_meeting_ids))
        all_meetings_by_id = {meeting.id: meeting for meeting in meetings}

    # Second pass: compile organization data with meeting information
    org_data = []
    for domain, members in organizations.items():
        action_items = []
        meeting_notes = []

        # Get meeting IDs for this domain
        meeting_ids = domain_meeting_ids[domain]

        # Process meetings for this domain
        for meeting_id in meeting_ids:
            meeting = all_meetings_by_id.get(meeting_id)
            if not meeting:
                continue

            # Process action items
            for item in meeting.action_items:
                if item.status.upper() != "COMPLETED":
                    action_items.append(
                        {
                            "id": item.id,
                            "title": item.title,
                            "description": item.description,
                            "status": item.status,
                            "assignee_name": item.assignee_name,
                            "assignee_email": item.assignee_email,
                            "meeting_id": meeting_id,
                            "meeting_name": meeting.name,
                        }
                    )

            # Process meeting notes
            if meeting.notes is not None:
                meeting_notes.append(
                    {
                        "meeting_id": meeting.id,
                        "meeting_name": meeting.name,
                        "created_at": meeting.created_at,
                        "notes": meeting.notes,
                    }
                )

        # Create organization data
        org_data.append(
            {
                "domain": domain,
                "display_name": (
                    domain if not members[0]["is_generic"] else members[0]["name"]
                ),
                "is_generic": members[0]["is_generic"],
                "members": sorted(members, key=lambda x: x["name"]),
                "member_count": len(members),
                "action_items": sorted(action_items, key=lambda x: x["status"]),
                "action_items_count": len(action_items),
                "meeting_notes": sorted(
                    meeting_notes, key=lambda x: x["created_at"], reverse=True
                ),
                "meeting_ids": list(meeting_ids),
            }
        )

    # Sort organizations by member count in descending order
    org_data.sort(key=lambda x: x["member_count"], reverse=True)
    return org_data
