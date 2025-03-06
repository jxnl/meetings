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

# Add more diverse speakers with various companies and roles
additional_speakers = [
    # Technology sector
    {"name": "Emily Zhang", "email": "emily.zhang@techfusion.com"},
    {"name": "Raj Patel", "email": "raj.patel@techfusion.com"},
    {"name": "Sophia Lee", "email": "sophia.lee@datanexus.io"},
    {"name": "Marcus Johnson", "email": "mjohnson@datanexus.io"},
    {"name": "Aiden Wilson", "email": "aiden@cloudsphere.com"},
    {"name": "Priya Sharma", "email": "priya.sharma@cloudsphere.com"},
    # Healthcare industry
    {"name": "Dr. James Wilson", "email": "jwilson@healthinnovate.org"},
    {"name": "Dr. Fatima Ahmed", "email": "fatima.ahmed@healthinnovate.org"},
    {"name": "Natalie Chen", "email": "nchen@medcentral.com"},
    {"name": "Robert Garcia", "email": "rgarcia@medcentral.com"},
    # Finance sector
    {"name": "Jonathan Hayes", "email": "jhayes@equitycapital.com"},
    {"name": "Amara Okafor", "email": "aokafor@equitycapital.com"},
    {"name": "Thomas Nakamura", "email": "tnakamura@globalfinance.com"},
    {"name": "Zoe Blackwell", "email": "zblackwell@globalfinance.com"},
    # Retail industry
    {"name": "Liam Murphy", "email": "liam@retailpro.com"},
    {"name": "Isabella Rodriguez", "email": "isabella@retailpro.com"},
    {"name": "Ethan Park", "email": "ethan@shopglobal.com"},
    {"name": "Chloe Bennett", "email": "cbennett@shopglobal.com"},
    # Education sector
    {"name": "Professor Samuel Adams", "email": "sadams@learntech.edu"},
    {"name": "Dr. Mei Lin", "email": "mlin@learntech.edu"},
    {"name": "Victor Okonkwo", "email": "vokonkwo@edufuture.org"},
    {"name": "Gabriella Martinez", "email": "gmartinez@edufuture.org"},
    # Manufacturing sector
    {"name": "Carlos Mendez", "email": "carlos@industrialinnovations.com"},
    {"name": "Layla Washington", "email": "layla@industrialinnovations.com"},
    {"name": "Hiroshi Tanaka", "email": "htanaka@globalmanufacturing.com"},
    {"name": "Fiona Campbell", "email": "fcampbell@globalmanufacturing.com"},
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
    "id": 404,
    "name": "TechFusion Product Roadmap Review",
    "createdAt": datetime.now().isoformat(),
    "duration": 4500,
    "url": "https://example.com/meeting/404",
    "attendees": [
        {"name": "Emily Zhang", "email": "emily.zhang@techfusion.com"},
        {"name": "Raj Patel", "email": "raj.patel@techfusion.com"},
        {"name": "John Doe", "email": "john@example.com"},
        {"name": "Maria Garcia", "email": "maria@example.com"},
    ],
    "recordingUrl": "https://example.com/recording/404",
    "notes": "# TechFusion Product Roadmap\n\nDiscussed Q3-Q4 feature releases and integration timeline with client.",
    "actionItems": [
        {
            "title": "Share API documentation",
            "description": "Provide updated integration specs for mobile platform",
            "status": "PENDING",
            "assignee_name": "Raj Patel",
            "assignee_email": "raj.patel@techfusion.com",
        },
        {
            "title": "Schedule technical workshop",
            "description": "Set up hands-on session for implementation team",
            "status": "PENDING",
            "assignee_name": "Maria Garcia",
            "assignee_email": "maria@example.com",
        },
    ],
    "transcript": [
        {
            "speaker": "John Doe",
            "text": "Thanks for joining our product roadmap review with TechFusion. Today we'll discuss the upcoming feature releases.",
            "timestamp": 0.0,
        },
        {
            "speaker": "Emily Zhang",
            "text": "We're excited to share our vision for the next six months. Our goal is to revolutionize how users interact with the platform.",
            "timestamp": 15.3,
        },
        {
            "speaker": "Raj Patel",
            "text": "Let me walk through our technical architecture changes and how they'll support the new feature set.",
            "timestamp": 42.7,
        },
        {
            "speaker": "Maria Garcia",
            "text": "I'm particularly interested in the AI-powered recommendation engine you mentioned in our previous call.",
            "timestamp": 94.2,
        },
        {
            "speaker": "Emily Zhang",
            "text": "Absolutely. We've made significant improvements to the algorithm, increasing accuracy by 37% in our tests.",
            "timestamp": 110.5,
        },
        {
            "speaker": "John Doe",
            "text": "What kind of integration timeline are we looking at for these new features?",
            "timestamp": 145.8,
        },
        {
            "speaker": "Raj Patel",
            "text": "We're planning a phased rollout starting next month. The API endpoints will be available in three weeks for early testing.",
            "timestamp": 160.2,
        },
        {
            "speaker": "Maria Garcia",
            "text": "That works with our schedule. We should set up a technical workshop for our implementation team.",
            "timestamp": 185.9,
        },
        {
            "speaker": "Emily Zhang",
            "text": "Great idea. We'll also provide comprehensive documentation and support throughout the integration process.",
            "timestamp": 201.4,
        },
        {
            "speaker": "John Doe",
            "text": "Let's discuss resource allocation and timeline expectations in more detail.",
            "timestamp": 230.7,
        },
    ],
}

# Healthcare industry client meeting
payload5 = {
    "id": 505,
    "name": "Health Innovate EHR Implementation",
    "createdAt": datetime.now().isoformat(),
    "duration": 3900,
    "url": "https://example.com/meeting/505",
    "attendees": [
        {"name": "Dr. James Wilson", "email": "jwilson@healthinnovate.org"},
        {"name": "Dr. Fatima Ahmed", "email": "fatima.ahmed@healthinnovate.org"},
        {"name": "Sarah Chen", "email": "sarah@example.com"},
        {"name": "David Kim", "email": "david@example.com"},
        {"name": "Olivia Taylor", "email": "olivia@example.com"},
    ],
    "recordingUrl": "https://example.com/recording/505",
    "notes": "# EHR Implementation Planning\n\nReviewed compliance requirements and integration timeline for new electronic health records system.",
    "actionItems": [
        {
            "title": "Finalize data migration plan",
            "description": "Document strategy for secure patient record transfer",
            "status": "PENDING",
            "assignee_name": "Sarah Chen",
            "assignee_email": "sarah@example.com",
        },
        {
            "title": "Schedule staff training sessions",
            "description": "Coordinate with department heads for EHR training",
            "status": "PENDING",
            "assignee_name": "Dr. Fatima Ahmed",
            "assignee_email": "fatima.ahmed@healthinnovate.org",
        },
    ],
    "transcript": [
        {
            "speaker": "David Kim",
            "text": "Welcome everyone. Today we'll be discussing the implementation plan for the new electronic health records system at Health Innovate.",
            "timestamp": 0.0,
        },
        {
            "speaker": "Dr. James Wilson",
            "text": "Thank you. Our primary concern is ensuring HIPAA compliance throughout the transition while minimizing disruption to patient care.",
            "timestamp": 22.6,
        },
        {
            "speaker": "Sarah Chen",
            "text": "We've developed a comprehensive data migration strategy that addresses those concerns. Let me walk you through it.",
            "timestamp": 48.9,
        },
        {
            "speaker": "Dr. Fatima Ahmed",
            "text": "I'm worried about the learning curve for our clinical staff. Many of our physicians have expressed concerns about workflow disruptions.",
            "timestamp": 105.3,
        },
        {
            "speaker": "Olivia Taylor",
            "text": "That's why we've designed a phased training approach, starting with department champions who can then support their colleagues.",
            "timestamp": 130.7,
        },
        {
            "speaker": "Dr. James Wilson",
            "text": "What's the timeline for full implementation across all five of our facilities?",
            "timestamp": 162.4,
        },
        {
            "speaker": "David Kim",
            "text": "We're looking at a 12-week rollout, starting with the main hospital and then expanding to satellite clinics.",
            "timestamp": 178.9,
        },
        {
            "speaker": "Sarah Chen",
            "text": "Our team will be onsite throughout the process, providing 24/7 support during the critical transition periods.",
            "timestamp": 200.5,
        },
        {
            "speaker": "Dr. Fatima Ahmed",
            "text": "We'll need to coordinate training schedules carefully to ensure adequate staffing for patient care.",
            "timestamp": 225.8,
        },
        {
            "speaker": "Olivia Taylor",
            "text": "Absolutely. We can provide both in-person and virtual training options to accommodate different schedules.",
            "timestamp": 245.2,
        },
        {
            "speaker": "Dr. James Wilson",
            "text": "Let's also discuss contingency plans in case we encounter unexpected issues during the transition.",
            "timestamp": 271.6,
        },
    ],
}

# Financial services client meeting
payload6 = {
    "id": 606,
    "name": "Equity Capital Investment Strategy",
    "createdAt": datetime.now().isoformat(),
    "duration": 4800,
    "url": "https://example.com/meeting/606",
    "attendees": [
        {"name": "Jonathan Hayes", "email": "jhayes@equitycapital.com"},
        {"name": "Amara Okafor", "email": "aokafor@equitycapital.com"},
        {"name": "Alex Johnson", "email": "alex@example.com"},
        {"name": "Jane Smith", "email": "jane@example.com"},
    ],
    "recordingUrl": "https://example.com/recording/606",
    "notes": "# Investment Strategy Session\n\nDiscussed market trends and portfolio optimization for Q3-Q4 investment approach.",
    "actionItems": [
        {
            "title": "Prepare risk assessment report",
            "description": "Analyze exposure across emerging markets",
            "status": "PENDING",
            "assignee_name": "Amara Okafor",
            "assignee_email": "aokafor@equitycapital.com",
        },
        {
            "title": "Schedule follow-up on regulatory compliance",
            "description": "Review recent changes to SEC guidelines",
            "status": "PENDING",
            "assignee_name": "Jane Smith",
            "assignee_email": "jane@example.com",
        },
    ],
    "transcript": [
        {
            "speaker": "Jane Smith",
            "text": "I'd like to welcome Equity Capital to our investment strategy session. We've prepared an analysis of current market conditions.",
            "timestamp": 0.0,
        },
        {
            "speaker": "Jonathan Hayes",
            "text": "Thank you. We're particularly interested in understanding how the recent Fed policy changes might impact our portfolio allocation strategy.",
            "timestamp": 25.4,
        },
        {
            "speaker": "Alex Johnson",
            "text": "Our analysis suggests shifting 15% of holdings from growth to value stocks given the current interest rate trajectory.",
            "timestamp": 58.7,
        },
        {
            "speaker": "Amara Okafor",
            "text": "That's aligned with our internal models. We're also looking at increasing our position in renewable energy, particularly in emerging markets.",
            "timestamp": 93.2,
        },
        {
            "speaker": "Jane Smith",
            "text": "We've prepared a detailed sector analysis. Renewable energy shows promising growth, but there are regulatory risks to consider.",
            "timestamp": 125.6,
        },
        {
            "speaker": "Jonathan Hayes",
            "text": "What's your perspective on the European market given the current geopolitical tensions?",
            "timestamp": 160.9,
        },
        {
            "speaker": "Alex Johnson",
            "text": "We're cautiously optimistic but recommending a more conservative approach in the short-term, with a focus on stable economies like Germany and the Nordics.",
            "timestamp": 178.3,
        },
        {
            "speaker": "Amara Okafor",
            "text": "We should also discuss our ESG integration strategy. Our clients are increasingly prioritizing sustainability metrics.",
            "timestamp": 220.7,
        },
        {
            "speaker": "Jane Smith",
            "text": "We've developed a proprietary ESG scoring system that we can apply to your portfolio. It's been effective at identifying both risks and opportunities.",
            "timestamp": 245.8,
        },
        {
            "speaker": "Jonathan Hayes",
            "text": "That would be valuable. We're facing more questions from our stakeholders about the environmental impact of our investments.",
            "timestamp": 275.3,
        },
        {
            "speaker": "Alex Johnson",
            "text": "Let's schedule a deeper dive on the ESG methodology next week. We can bring in our sustainability specialist.",
            "timestamp": 296.1,
        },
    ],
}

# Education technology client meeting
payload7 = {
    "id": 707,
    "name": "LearnTech Curriculum Integration",
    "createdAt": datetime.now().isoformat(),
    "duration": 4200,
    "url": "https://example.com/meeting/707",
    "attendees": [
        {"name": "Professor Samuel Adams", "email": "sadams@learntech.edu"},
        {"name": "Dr. Mei Lin", "email": "mlin@learntech.edu"},
        {"name": "Michael Brown", "email": "michael@example.com"},
        {"name": "Maria Garcia", "email": "maria@example.com"},
    ],
    "recordingUrl": "https://example.com/recording/707",
    "notes": "# Educational Technology Integration\n\nPlanned implementation of adaptive learning platform across undergraduate science programs.",
    "actionItems": [
        {
            "title": "Develop faculty training program",
            "description": "Create resources for instructors on platform features",
            "status": "PENDING",
            "assignee_name": "Michael Brown",
            "assignee_email": "michael@example.com",
        },
        {
            "title": "Map curriculum outcomes to platform content",
            "description": "Ensure alignment with learning objectives",
            "status": "PENDING",
            "assignee_name": "Dr. Mei Lin",
            "assignee_email": "mlin@learntech.edu",
        },
    ],
    "transcript": [
        {
            "speaker": "Maria Garcia",
            "text": "Welcome to our session on integrating the adaptive learning platform into LearnTech's curriculum. We're excited to collaborate on this initiative.",
            "timestamp": 0.0,
        },
        {
            "speaker": "Professor Samuel Adams",
            "text": "We're looking forward to enhancing our science programs with this technology. Our biology department has been particularly enthusiastic about the possibilities.",
            "timestamp": 28.3,
        },
        {
            "speaker": "Dr. Mei Lin",
            "text": "Our main priority is ensuring the platform supports our learning outcomes while providing meaningful data on student progress.",
            "timestamp": 55.7,
        },
        {
            "speaker": "Michael Brown",
            "text": "I'll demonstrate how the analytics dashboard can help track student mastery of key concepts and identify areas where additional support is needed.",
            "timestamp": 85.2,
        },
        {
            "speaker": "Professor Samuel Adams",
            "text": "This level of insight would be tremendously helpful. Currently, we often don't realize students are struggling until after the midterm exams.",
            "timestamp": 136.8,
        },
        {
            "speaker": "Maria Garcia",
            "text": "The platform also allows you to create custom intervention strategies when the system flags a student who might be falling behind.",
            "timestamp": 165.3,
        },
        {
            "speaker": "Dr. Mei Lin",
            "text": "How customizable is the content? We have some unique laboratory simulations that we'd like to incorporate.",
            "timestamp": 192.7,
        },
        {
            "speaker": "Michael Brown",
            "text": "The platform supports integration of third-party content, including virtual labs. We can schedule a technical session to review your specific requirements.",
            "timestamp": 210.4,
        },
        {
            "speaker": "Professor Samuel Adams",
            "text": "What support will be available for our faculty during implementation? Many are enthusiastic but concerned about the learning curve.",
            "timestamp": 245.9,
        },
        {
            "speaker": "Maria Garcia",
            "text": "We provide comprehensive training sessions and ongoing support. We also recommend identifying department champions who can serve as local experts.",
            "timestamp": 270.3,
        },
        {
            "speaker": "Dr. Mei Lin",
            "text": "Let's discuss the timeline for implementation. We'd like to pilot this in the spring semester with full deployment next fall.",
            "timestamp": 305.8,
        },
    ],
}

# Manufacturing industry client meeting
payload8 = {
    "id": 808,
    "name": "Industrial Innovations Automation Project",
    "createdAt": datetime.now().isoformat(),
    "duration": 5100,
    "url": "https://example.com/meeting/808",
    "attendees": [
        {"name": "Carlos Mendez", "email": "carlos@industrialinnovations.com"},
        {"name": "Layla Washington", "email": "layla@industrialinnovations.com"},
        {"name": "David Kim", "email": "david@example.com"},
        {"name": "Olivia Taylor", "email": "olivia@example.com"},
        {"name": "Alex Johnson", "email": "alex@example.com"},
    ],
    "recordingUrl": "https://example.com/recording/808",
    "notes": "# Factory Automation Project\n\nReviewed implementation plan for robotic assembly line and IoT sensor network.",
    "actionItems": [
        {
            "title": "Complete site assessment",
            "description": "Evaluate factory floor layout for optimal sensor placement",
            "status": "PENDING",
            "assignee_name": "Alex Johnson",
            "assignee_email": "alex@example.com",
        },
        {
            "title": "Develop employee training plan",
            "description": "Create resources for floor workers on new automated systems",
            "status": "PENDING",
            "assignee_name": "Layla Washington",
            "assignee_email": "layla@industrialinnovations.com",
        },
    ],
    "transcript": [
        {
            "speaker": "David Kim",
            "text": "Thank you for joining today's meeting to discuss the automation project for Industrial Innovations' manufacturing facility.",
            "timestamp": 0.0,
        },
        {
            "speaker": "Carlos Mendez",
            "text": "We're eager to improve our production efficiency. Our current manual processes are creating bottlenecks as customer demand increases.",
            "timestamp": 20.5,
        },
        {
            "speaker": "Alex Johnson",
            "text": "Based on our initial assessment, we believe implementing robotic assembly stations for the primary production line could increase throughput by 35%.",
            "timestamp": 45.8,
        },
        {
            "speaker": "Layla Washington",
            "text": "That's significant. How will this impact our current workforce? We want to ensure a smooth transition with minimal disruption.",
            "timestamp": 78.2,
        },
        {
            "speaker": "Olivia Taylor",
            "text": "Our implementation plan includes a comprehensive training program to upskill your team. Many manual roles will transition to system operators and quality control.",
            "timestamp": 102.7,
        },
        {
            "speaker": "Carlos Mendez",
            "text": "What kind of timeline are we looking at for full implementation? Our busiest season starts in four months.",
            "timestamp": 145.3,
        },
        {
            "speaker": "David Kim",
            "text": "We're proposing a phased approach over 16 weeks, with critical systems in place before your peak period. We can prioritize the highest-impact areas first.",
            "timestamp": 160.9,
        },
        {
            "speaker": "Alex Johnson",
            "text": "The IoT sensor network will provide real-time production analytics and predictive maintenance capabilities, which should reduce downtime by approximately 20%.",
            "timestamp": 195.4,
        },
        {
            "speaker": "Layla Washington",
            "text": "Maintenance efficiency is a key concern for us. Our current reactive approach leads to significant production delays.",
            "timestamp": 228.7,
        },
        {
            "speaker": "Olivia Taylor",
            "text": "The system will identify potential equipment failures before they occur, allowing for scheduled maintenance during non-peak hours.",
            "timestamp": 250.2,
        },
        {
            "speaker": "Carlos Mendez",
            "text": "What about integration with our existing ERP system? We need seamless data flow for inventory management.",
            "timestamp": 282.6,
        },
        {
            "speaker": "David Kim",
            "text": "We've reviewed your ERP documentation and developed custom APIs to ensure complete integration. All production data will sync automatically.",
            "timestamp": 300.1,
        },
    ],
}

# Retail industry client meeting
payload9 = {
    "id": 909,
    "name": "RetailPro Omnichannel Strategy",
    "createdAt": datetime.now().isoformat(),
    "duration": 3600,
    "url": "https://example.com/meeting/909",
    "attendees": [
        {"name": "Liam Murphy", "email": "liam@retailpro.com"},
        {"name": "Isabella Rodriguez", "email": "isabella@retailpro.com"},
        {"name": "Jane Smith", "email": "jane@example.com"},
        {"name": "Michael Brown", "email": "michael@example.com"},
    ],
    "recordingUrl": "https://example.com/recording/909",
    "notes": "# Omnichannel Retail Strategy\n\nPlanned integration of online and in-store experiences for seamless customer journey.",
    "actionItems": [
        {
            "title": "Finalize inventory synchronization plan",
            "description": "Ensure real-time stock visibility across all channels",
            "status": "PENDING",
            "assignee_name": "Michael Brown",
            "assignee_email": "michael@example.com",
        },
        {
            "title": "Develop customer journey maps",
            "description": "Document key touchpoints across digital and physical shopping experiences",
            "status": "PENDING",
            "assignee_name": "Isabella Rodriguez",
            "assignee_email": "isabella@retailpro.com",
        },
    ],
    "transcript": [
        {
            "speaker": "Jane Smith",
            "text": "Thanks for joining our omnichannel strategy session for RetailPro. Today we'll focus on creating a seamless experience between your online platform and physical stores.",
            "timestamp": 0.0,
        },
        {
            "speaker": "Liam Murphy",
            "text": "This is a top priority for us. Our customers are increasingly starting their shopping online and finishing in-store, or vice versa.",
            "timestamp": 30.2,
        },
        {
            "speaker": "Michael Brown",
            "text": "Our analysis of your current customer journey identified several friction points, particularly around inventory visibility and fulfillment options.",
            "timestamp": 60.8,
        },
        {
            "speaker": "Isabella Rodriguez",
            "text": "That's exactly right. Customers get frustrated when they see a product online but can't find it in their local store, or when store associates can't access online order history.",
            "timestamp": 92.5,
        },
        {
            "speaker": "Jane Smith",
            "text": "We're proposing a unified commerce platform that provides real-time inventory across channels and a single view of the customer regardless of touchpoint.",
            "timestamp": 125.7,
        },
        {
            "speaker": "Liam Murphy",
            "text": "How complex is the integration with our existing POS and e-commerce systems? We've invested heavily in both platforms.",
            "timestamp": 158.3,
        },
        {
            "speaker": "Michael Brown",
            "text": "We've developed a middleware solution that connects these systems without replacing them. It creates a data layer that synchronizes in real-time.",
            "timestamp": 180.9,
        },
        {
            "speaker": "Isabella Rodriguez",
            "text": "What about our loyalty program? We need to ensure customers receive consistent benefits regardless of channel.",
            "timestamp": 215.4,
        },
        {
            "speaker": "Jane Smith",
            "text": "The platform includes a unified loyalty engine that works across all touchpoints. Customers can earn and redeem points seamlessly between online and in-store.",
            "timestamp": 235.8,
        },
        {
            "speaker": "Liam Murphy",
            "text": "This sounds promising. What kind of timeline and resource commitment should we expect for implementation?",
            "timestamp": 270.2,
        },
        {
            "speaker": "Michael Brown",
            "text": "We're looking at a 20-week implementation, starting with core inventory and customer data integration, then adding advanced features in phases.",
            "timestamp": 290.7,
        },
    ],
}

# Government sector client meeting
payload10 = {
    "id": 1010,
    "name": "Smart City Initiative Planning",
    "createdAt": datetime.now().isoformat(),
    "duration": 5400,
    "url": "https://example.com/meeting/1010",
    "attendees": [
        {"name": "Mayor Eleanor Jackson", "email": "mayor.jackson@metrocity.gov"},
        {"name": "Commissioner Terrence Wong", "email": "t.wong@metrocity.gov"},
        {"name": "Director Jasmine Richards", "email": "j.richards@metrocity.gov"},
        {"name": "John Doe", "email": "john@example.com"},
        {"name": "Sarah Chen", "email": "sarah@example.com"},
        {"name": "Alex Johnson", "email": "alex@example.com"},
    ],
    "recordingUrl": "https://example.com/recording/1010",
    "notes": "# Smart City Initiative\n\nDiscussed implementation plan for urban IoT network and data analytics platform for city services optimization.",
    "actionItems": [
        {
            "title": "Prepare privacy impact assessment",
            "description": "Evaluate data collection practices against privacy regulations",
            "status": "PENDING",
            "assignee_name": "Sarah Chen",
            "assignee_email": "sarah@example.com",
        },
        {
            "title": "Develop public engagement strategy",
            "description": "Create communication plan for residents about initiative benefits",
            "status": "PENDING",
            "assignee_name": "Director Jasmine Richards",
            "assignee_email": "j.richards@metrocity.gov",
        },
        {
            "title": "Draft phased implementation timeline",
            "description": "Prioritize neighborhoods and technologies for rollout",
            "status": "PENDING",
            "assignee_name": "Alex Johnson",
            "assignee_email": "alex@example.com",
        },
    ],
    "transcript": [
        {
            "speaker": "John Doe",
            "text": "Thank you for the opportunity to present our smart city infrastructure proposal for Metro City. We're excited about the potential impact on urban services.",
            "timestamp": 0.0,
        },
        {
            "speaker": "Mayor Eleanor Jackson",
            "text": "We're committed to making our city more responsive to residents' needs while improving sustainability. Technology will be key to achieving these goals.",
            "timestamp": 32.6,
        },
        {
            "speaker": "Sarah Chen",
            "text": "Our approach integrates IoT sensors, data analytics, and mobile services to create a connected urban ecosystem that optimizes everything from traffic flow to energy usage.",
            "timestamp": 65.9,
        },
        {
            "speaker": "Commissioner Terrence Wong",
            "text": "My primary concern is data security and privacy. We need robust protections for any information collected from citizens.",
            "timestamp": 105.3,
        },
        {
            "speaker": "Alex Johnson",
            "text": "Absolutely. Our platform is built with privacy-by-design principles. All personally identifiable information is either anonymized or not collected at all.",
            "timestamp": 130.8,
        },
        {
            "speaker": "Director Jasmine Richards",
            "text": "What about accessibility? We serve a diverse population with varying levels of technological literacy and access.",
            "timestamp": 170.2,
        },
        {
            "speaker": "John Doe",
            "text": "Great point. We've designed multiple interfaces, including physical kiosks, mobile apps, and traditional web portals to ensure all residents can benefit.",
            "timestamp": 195.7,
        },
        {
            "speaker": "Mayor Eleanor Jackson",
            "text": "Let's discuss implementation costs and timeline. Our budget cycle requires careful planning for multi-year projects.",
            "timestamp": 240.3,
        },
        {
            "speaker": "Sarah Chen",
            "text": "We've developed a phased approach that allows for modular implementation, beginning with high-impact, low-cost components like smart street lighting and traffic management.",
            "timestamp": 265.8,
        },
        {
            "speaker": "Commissioner Terrence Wong",
            "text": "What kind of ROI can we expect? The council will want clear metrics on how this investment benefits residents.",
            "timestamp": 300.4,
        },
        {
            "speaker": "Alex Johnson",
            "text": "Our analysis of similar implementations shows an average 15% reduction in energy costs, 12% improvement in emergency response times, and significant reductions in traffic congestion.",
            "timestamp": 325.9,
        },
        {
            "speaker": "Director Jasmine Richards",
            "text": "We'll need a robust public engagement strategy. Residents should understand how this initiative improves their daily lives.",
            "timestamp": 360.5,
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
    "7": payload7,
    "8": payload8,
    "9": payload9,
    "10": payload10,
}


import asyncio
import aiohttp


async def main():
    """Send all webhook payloads to the API asynchronously."""
    # Check if a specific payload was requested
    if len(sys.argv) > 1 and sys.argv[1] in payloads:
        payload_id = sys.argv[1]
        await send_payload(payload_id, payloads[payload_id])
    else:
        # Send all payloads
        print(f"Sending all {len(payloads)} webhook payloads to: {WEBHOOK_URL}")
        tasks = []
        for payload_id, payload in payloads.items():
            print("\n" + "-" * 50)
            tasks.append(send_payload(payload_id, payload))

        await asyncio.gather(*tasks)


async def send_payload(payload_id, payload):
    """Send a single webhook payload to the API asynchronously."""
    print(f"Using payload {payload_id}: {payload['name']}")
    print(f"Attendees: {len(payload['attendees'])} people")
    print("Sending webhook payload to:", WEBHOOK_URL)

    try:
        # Convert datetime objects to strings for JSON serialization
        payload_json = json.dumps(payload, default=str)

        # Send the webhook payload
        async with aiohttp.ClientSession() as session:
            async with session.post(
                WEBHOOK_URL,
                data=payload_json,
                headers={"Content-Type": "application/json"},
            ) as response:
                status_code = response.status
                if status_code < 400:
                    response_data = await response.json()
                    response_text = json.dumps(response_data, indent=2)
                else:
                    response_text = await response.text()

                # Print the response
                print(f"Status code: {status_code}")
                print("Response:")
                print(response_text)

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
