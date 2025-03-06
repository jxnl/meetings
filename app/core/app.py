"""
FastAPI application factory and configuration.
"""

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import api_router
from app.api.routes.meetings import route as meetings_router
from app.core.config import settings


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured FastAPI application instance
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.VERSION,
        openapi_url=f"{settings.API_PREFIX}/openapi.json",
        docs_url=f"{settings.API_PREFIX}/docs",
        redoc_url=f"{settings.API_PREFIX}/redoc",
    )

    # Set up CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API router (for backend functionality)
    app.include_router(api_router, prefix=settings.API_PREFIX)

    # Create a separate UI router for the web interface
    ui_router = APIRouter()

    # Add meetings UI routes to the UI router
    ui_router.include_router(
        meetings_router.router, prefix="/meetings", tags=["meetings-ui"]
    )

    # Include UI router at root level (no prefix)
    app.include_router(ui_router)

    # Mount static files
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

    @app.get("/")
    async def root():
        """Root endpoint that redirects to API documentation."""
        return {"message": "Welcome to the API. Visit /api/docs for documentation."}

    return app
