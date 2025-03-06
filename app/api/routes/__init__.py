"""
API routes package initialization.
"""

from fastapi import APIRouter

from app.api.routes import webhooks

# Create main API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])

# Add more routers here as needed
# api_router.include_router(users.router, prefix="/users", tags=["users"])
