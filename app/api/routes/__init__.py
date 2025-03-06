"""
API routes package initialization.
"""

from fastapi import APIRouter

from app.api.routes import webhooks
from app.api.routes.meetings import route as meetings

# Create main API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
api_router.include_router(meetings.router, prefix="/meetings", tags=["meetings-api"])

# Add more routers here as needed
# api_router.include_router(users.router, prefix="/users", tags=["users"])
