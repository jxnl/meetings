"""
Test script to send a webhook payload to the API.
"""

import json
import requests
import sys
from datetime import datetime

# Webhook endpoint URL
WEBHOOK_URL = "http://localhost:8000/api/webhooks/"

# Example webhook payloads
payload1 = {
    "id": 123,
    "name": "Team Meeting",
    "createdAt": datetime.now().isoformat(),
    "duration": 3600,
    "url": "https://example.com/meeting/123",
    "attendees": [
        {"name": "John Doe", "email": "john@example.com"},
        {"name": "Jane Smith", "email": "jane@example.com"},
    ],
    "recordingUrl": "https://example.com/recording/123",
    "notes": "# Meeting Notes\n\nThis is a test meeting with notes in markdown format.",
    "actionItems": [
        {
            "title": "Research new feature",
            "description": "Look into implementing the new feature",
            "status": "PENDING",
            "assignee_name": "John Doe",
            "assignee_email": "john@example.com",
        }
    ],
    "transcript": [
        {
            "speaker": "John Doe",
            "text": "Hello everyone, welcome to the meeting.",
            "timestamp": 0.0,
        },
        {
            "speaker": "Jane Smith",
            "text": "Thanks for organizing this.",
            "timestamp": 10.5,
        },
    ],
}

# Product Development Meeting payload
payload2 = {
    "id": 456,
    "name": "Product Development Meeting",
    "createdAt": datetime.now().isoformat(),
    "duration": 2700,
    "url": "https://example.com/meeting/456",
    "attendees": [
        {"name": "Alex Johnson", "email": "alex@example.com"},
        {"name": "Maria Garcia", "email": "maria@example.com"},
        {"name": "David Kim", "email": "david@example.com"},
        {"name": "Sarah Chen", "email": "sarah@example.com"},
    ],
    "recordingUrl": "https://example.com/recording/456",
    "notes": "# Product Development\n\nDiscussed roadmap for Q3 and feature prioritization.",
    "actionItems": [
        {
            "title": "Update roadmap document",
            "description": "Incorporate feedback from stakeholders",
            "status": "PENDING",
            "assignee_name": "Maria Garcia",
            "assignee_email": "maria@example.com",
        }
    ],
    "transcript": [
        {
            "speaker": "Alex Johnson",
            "text": "Let's review our progress on the current sprint.",
            "timestamp": 0.0,
        },
        {
            "speaker": "Maria Garcia",
            "text": "We've completed 80% of our planned tasks.",
            "timestamp": 15.2,
        },
    ],
}

# Marketing Strategy Meeting payload
payload3 = {
    "id": 789,
    "name": "Marketing Strategy Meeting",
    "createdAt": datetime.now().isoformat(),
    "duration": 4500,
    "url": "https://example.com/meeting/789",
    "attendees": [
        {"name": "Emma Wilson", "email": "maria@example.com"},
        {"name": "Michael Brown", "email": "michael@example.com"},
        {"name": "Olivia Taylor", "email": "olivia@example.com"},
    ],
    "recordingUrl": "https://example.com/recording/789",
    "notes": "# Marketing Strategy\n\nReviewed campaign performance and discussed upcoming product launch.",
    "actionItems": [
        {
            "title": "Prepare social media assets",
            "description": "Create graphics and copy for launch campaign",
            "status": "PENDING",
            "assignee_name": "Olivia Taylor",
            "assignee_email": "olivia@example.com",
        }
    ],
    "transcript": [
        {
            "speaker": "Maria Garcia",
            "text": "Our last campaign exceeded expectations by 15%.",
            "timestamp": 0.0,
        },
        {
            "speaker": "Michael Brown",
            "text": "Great results! Let's apply those learnings to our next launch.",
            "timestamp": 12.8,
        },
    ],
}

# Client Onboarding Meeting payload
payload4 = {
    "id": 101,
    "name": "Client Onboarding Meeting",
    "createdAt": datetime.now().isoformat(),
    "duration": 1800,
    "url": "https://example.com/meeting/101",
    "attendees": [
        {"name": "Robert Lee", "email": "robert@example.com"},
        {"name": "Jennifer Lopez", "email": "jennifer@example.com"},
        {"name": "Thomas Wright", "email": "thomas@example.com"},
        {"name": "Lisa Johnson", "email": "lisa@clientcompany.com"},
        {"name": "Kevin Chen", "email": "kevin@clientcompany.com"},
    ],
    "recordingUrl": "https://example.com/recording/101",
    "notes": "# Client Onboarding\n\nIntroduced our team and discussed project timeline and deliverables.",
    "actionItems": [
        {
            "title": "Send follow-up documentation",
            "description": "Share onboarding materials and next steps",
            "status": "PENDING",
            "assignee_name": "Jennifer Lopez",
            "assignee_email": "jennifer@example.com",
        }
    ],
    "transcript": [
        {
            "speaker": "Robert Lee",
            "text": "Welcome to our team! We're excited to work with you.",
            "timestamp": 0.0,
        },
        {
            "speaker": "Lisa Johnson",
            "text": "Thank you for having us. We're looking forward to this partnership.",
            "timestamp": 8.3,
        },
    ],
}

# Dictionary of available payloads
payloads = {
    "1": payload1,
    "2": payload2,
    "3": payload3,
    "4": payload4,
}


def main():
    """Send the webhook payload to the API."""
    # Determine which payload to use
    payload_id = "1"  # Default to first payload

    if len(sys.argv) > 1 and sys.argv[1] in payloads:
        payload_id = sys.argv[1]

    payload = payloads[payload_id]

    print(f"Using payload {payload_id}: {payload['name']}")
    print(f"Attendees: {len(payload['attendees'])} people")
    print("Sending webhook payload to:", WEBHOOK_URL)

    try:
        # Convert datetime objects to strings for JSON serialization
        payload_json = json.dumps(payload, default=str)

        # Send the webhook payload
        response = requests.post(
            WEBHOOK_URL, data=payload_json, headers={"Content-Type": "application/json"}
        )

        # Print the response
        print(f"Status code: {response.status_code}")
        print("Response:")
        print(
            json.dumps(response.json(), indent=2)
            if response.status_code < 400
            else response.text
        )

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
