"""
Application configuration settings loaded from environment variables.
"""

from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Attributes:
        PROJECT_NAME: Name of the project
        PROJECT_DESCRIPTION: Description of the project
        VERSION: API version
        API_PREFIX: Prefix for all API endpoints
        CORS_ORIGINS: List of allowed origins for CORS
        DATABASE_URL: Database connection string
        DIRECT_URL: Direct database connection string for migrations
    """

    PROJECT_NAME: str = "FastAPI Application"
    PROJECT_DESCRIPTION: str = "A simple FastAPI application"
    VERSION: str = "0.1.0"
    API_PREFIX: str = "/api"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Database settings
    DATABASE_URL: str
    DIRECT_URL: str

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


# Create settings instance
settings = Settings()
