"""
Test script to send a webhook payload to the API.
"""

import json
import requests
import sys
import random
from datetime import datetime

# Webhook endpoint URL
WEBHOOK_URL = "http://localhost:8000/api/webhooks/"

# Common speakers across meetings for realistic overlap
common_speakers = [
    {"name": "John Doe", "email": "john@example.com"},
    {"name": "Jane Smith", "email": "jane@example.com"},
    {"name": "Maria Garcia", "email": "maria@example.com"},
    {"name": "Alex Johnson", "email": "alex@example.com"},
    {"name": "David Kim", "email": "david@example.com"},
    {"name": "Sarah Chen", "email": "sarah@example.com"},
    {"name": "Michael Brown", "email": "michael@example.com"},
    {"name": "Olivia Taylor", "email": "olivia@example.com"},
]

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
        {"name": "Maria Garcia", "email": "maria@example.com"},
        {"name": "Alex Johnson", "email": "alex@example.com"},
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
            "text": "Hello everyone, welcome to the team meeting.",
            "timestamp": 0.0,
        },
        {
            "speaker": "Jane Smith",
            "text": "Thanks for organizing this, John.",
            "timestamp": 10.5,
        },
        {
            "speaker": "Maria Garcia",
            "text": "I've prepared some updates on the current project status.",
            "timestamp": 25.2,
        },
        {
            "speaker": "Alex Johnson",
            "text": "Great, I'm particularly interested in the timeline adjustments.",
            "timestamp": 42.8,
        },
        {
            "speaker": "John Doe",
            "text": "Let's go through the agenda items one by one.",
            "timestamp": 58.3,
        },
        {
            "speaker": "Maria Garcia",
            "text": "We've made significant progress on the backend integration.",
            "timestamp": 75.1,
        },
        {
            "speaker": "Jane Smith",
            "text": "The user testing results came in yesterday, and they're quite positive.",
            "timestamp": 92.6,
        },
        {
            "speaker": "Alex Johnson",
            "text": "That's excellent news. Any specific feedback we should address?",
            "timestamp": 110.4,
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
        {
            "speaker": "David Kim",
            "text": "The new authentication system is ready for testing.",
            "timestamp": 32.7,
        },
        {
            "speaker": "Sarah Chen",
            "text": "I've identified some potential performance bottlenecks we should address.",
            "timestamp": 48.9,
        },
        {
            "speaker": "Alex Johnson",
            "text": "Good catch, Sarah. Let's prioritize those for the next sprint.",
            "timestamp": 65.3,
        },
        {
            "speaker": "Maria Garcia",
            "text": "I agree. We should also consider the user feedback from the beta testers.",
            "timestamp": 82.1,
        },
        {
            "speaker": "David Kim",
            "text": "The UX team has some suggestions for improving the onboarding flow.",
            "timestamp": 98.6,
        },
        {
            "speaker": "Sarah Chen",
            "text": "I can work with them to implement those changes by next week.",
            "timestamp": 115.0,
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
        {"name": "Maria Garcia", "email": "maria@example.com"},
        {"name": "Michael Brown", "email": "michael@example.com"},
        {"name": "Olivia Taylor", "email": "olivia@example.com"},
        {"name": "John Doe", "email": "john@example.com"},
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
        {
            "speaker": "Olivia Taylor",
            "text": "I've drafted a content calendar for the next quarter.",
            "timestamp": 28.5,
        },
        {
            "speaker": "John Doe",
            "text": "The product team has provided the key features we should highlight.",
            "timestamp": 45.2,
        },
        {
            "speaker": "Maria Garcia",
            "text": "Perfect. We should focus on the AI capabilities in our messaging.",
            "timestamp": 62.7,
        },
        {
            "speaker": "Michael Brown",
            "text": "Our competitors are also emphasizing AI. We need a unique angle.",
            "timestamp": 80.1,
        },
        {
            "speaker": "Olivia Taylor",
            "text": "What about highlighting the user experience improvements?",
            "timestamp": 95.6,
        },
        {
            "speaker": "John Doe",
            "text": "That's a good approach. We have some compelling user testimonials we can use.",
            "timestamp": 112.3,
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
        {
            "speaker": "Jennifer Lopez",
            "text": "I'll be your main point of contact throughout the implementation.",
            "timestamp": 20.5,
        },
        {
            "speaker": "Kevin Chen",
            "text": "Could you walk us through the typical timeline for implementation?",
            "timestamp": 35.2,
        },
        {
            "speaker": "Thomas Wright",
            "text": "Certainly. We usually complete the initial setup within two weeks.",
            "timestamp": 48.7,
        },
        {
            "speaker": "Lisa Johnson",
            "text": "That's faster than we expected. What do you need from our side?",
            "timestamp": 65.1,
        },
        {
            "speaker": "Jennifer Lopez",
            "text": "We'll need access to your current systems and data formats.",
            "timestamp": 80.6,
        },
        {
            "speaker": "Kevin Chen",
            "text": "I'll make sure our IT team provides everything you need by tomorrow.",
            "timestamp": 95.3,
        },
    ],
}

# Technical Review Meeting with overlapping speakers
payload5 = {
    "id": 202,
    "name": "Technical Review Meeting",
    "createdAt": datetime.now().isoformat(),
    "duration": 3300,
    "url": "https://example.com/meeting/202",
    "attendees": [
        {"name": "David Kim", "email": "david@example.com"},
        {"name": "Sarah Chen", "email": "sarah@example.com"},
        {"name": "Alex Johnson", "email": "alex@example.com"},
        {"name": "Michael Brown", "email": "michael@example.com"},
    ],
    "recordingUrl": "https://example.com/recording/202",
    "notes": "# Technical Review\n\nReviewed architecture decisions and technical debt priorities.",
    "actionItems": [
        {
            "title": "Refactor authentication module",
            "description": "Address security concerns and improve performance",
            "status": "PENDING",
            "assignee_name": "David Kim",
            "assignee_email": "david@example.com",
        }
    ],
    "transcript": [
        {
            "speaker": "David Kim",
            "text": "Let's review the architecture changes proposed last week.",
            "timestamp": 0.0,
        },
        {
            "speaker": "Sarah Chen",
            "text": "I've analyzed the performance implications of the new database schema.",
            "timestamp": 15.7,
        },
        {
            "speaker": "Alex Johnson",
            "text": "How significant are the improvements?",
            "timestamp": 30.2,
        },
        {
            "speaker": "Sarah Chen",
            "text": "We're seeing a 40% reduction in query times for the most common operations.",
            "timestamp": 42.8,
        },
        {
            "speaker": "Michael Brown",
            "text": "That's impressive. What about the migration plan?",
            "timestamp": 58.5,
        },
        {
            "speaker": "David Kim",
            "text": "I've drafted a phased approach to minimize downtime.",
            "timestamp": 72.1,
        },
        {
            "speaker": "Alex Johnson",
            "text": "We should also consider the impact on the frontend team's work.",
            "timestamp": 88.6,
        },
        {
            "speaker": "Michael Brown",
            "text": "Good point. Let's schedule a joint session with them next week.",
            "timestamp": 105.3,
        },
    ],
}

# Quarterly Planning Meeting with overlapping speakers
payload6 = {
    "id": 303,
    "name": "Quarterly Planning Meeting",
    "createdAt": datetime.now().isoformat(),
    "duration": 5400,
    "url": "https://example.com/meeting/303",
    "attendees": [
        {"name": "John Doe", "email": "john@example.com"},
        {"name": "Maria Garcia", "email": "maria@example.com"},
        {"name": "Olivia Taylor", "email": "olivia@example.com"},
        {"name": "David Kim", "email": "david@example.com"},
        {"name": "Jane Smith", "email": "jane@example.com"},
    ],
    "recordingUrl": "https://example.com/recording/303",
    "notes": "# Quarterly Planning\n\nSet objectives for Q3 and reviewed resource allocation.",
    "actionItems": [
        {
            "title": "Finalize Q3 OKRs",
            "description": "Document and distribute final objectives and key results",
            "status": "PENDING",
            "assignee_name": "John Doe",
            "assignee_email": "john@example.com",
        }
    ],
    "transcript": [
        {
            "speaker": "John Doe",
            "text": "Welcome to our quarterly planning session. Let's start with a review of Q2 results.",
            "timestamp": 0.0,
        },
        {
            "speaker": "Maria Garcia",
            "text": "We achieved 85% of our objectives for Q2, with notable success in the mobile initiative.",
            "timestamp": 18.3,
        },
        {
            "speaker": "Olivia Taylor",
            "text": "The marketing campaigns exceeded our targets by 20%.",
            "timestamp": 35.7,
        },
        {
            "speaker": "David Kim",
            "text": "The engineering team completed the platform migration ahead of schedule.",
            "timestamp": 52.1,
        },
        {
            "speaker": "Jane Smith",
            "text": "Customer satisfaction scores improved by 15 points since our last measurement.",
            "timestamp": 68.9,
        },
        {
            "speaker": "John Doe",
            "text": "These are excellent results. Now let's discuss our priorities for Q3.",
            "timestamp": 85.4,
        },
        {
            "speaker": "Maria Garcia",
            "text": "I propose we focus on expanding our enterprise offerings.",
            "timestamp": 102.8,
        },
        {
            "speaker": "Olivia Taylor",
            "text": "We should also consider increasing our content marketing efforts.",
            "timestamp": 120.5,
        },
    ],
}

# Dictionary of available payloads
payloads = {
    "1": payload1,
    "2": payload2,
    "3": payload3,
    "4": payload4,
    "5": payload5,
    "6": payload6,
}


def main():
    """Send all webhook payloads to the API."""
    # Check if a specific payload was requested
    if len(sys.argv) > 1 and sys.argv[1] in payloads:
        payload_id = sys.argv[1]
        send_payload(payload_id, payloads[payload_id])
    else:
        # Send all payloads
        print(f"Sending all {len(payloads)} webhook payloads to: {WEBHOOK_URL}")
        for payload_id, payload in payloads.items():
            print("\n" + "-" * 50)
            send_payload(payload_id, payload)


def send_payload(payload_id, payload):
    """Send a single webhook payload to the API."""
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
