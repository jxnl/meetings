"""
Test script to send a webhook payload to the API.
"""

import json
import requests
from datetime import datetime

# Webhook endpoint URL
WEBHOOK_URL = "http://localhost:8000/api/webhooks/"

# Example webhook payload
payload = {
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


def main():
    """Send the webhook payload to the API."""
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
