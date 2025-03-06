# Meetings App - Developer Guide

## Common Commands
- Start server: `uvicorn main:app --reload`
- Initialize database: `python init_db.py`
- Test webhook: `python test_webhook.py` or `python test_webhook.py 1` (for specific payload)
- API docs: http://localhost:8000/api/docs
- Database migrations: `alembic revision --autogenerate -m "message"` and `alembic upgrade head`

## Code Style Guidelines
- Use type hints for all function parameters and return values
- Follow PEP 8 conventions for Python code
- Structure imports: standard lib, third-party, local (alphabetical in each group)
- Use descriptive variable/function names in snake_case
- Document all functions with docstrings (Google style)
- Handle exceptions with specific error types and meaningful messages
- Models use SQLAlchemy; schemas use Pydantic
- Keep business logic in service layer, not in routes
- Use dependency injection for database sessions

## Architecture
- FastAPI web framework with SQLAlchemy ORM (PostgreSQL)
- Routes → Services → Models pattern
- Webhooks receive meeting data and store in database
- UI templates for displaying and exporting meeting data

## Database Models
- Meeting: Core entity with meeting metadata
- Attendee: Unique attendees with name/email (many-to-many with meetings)
- ActionItem: Tasks/action items from meetings
- TranscriptEntry: Meeting transcript with speaker text and timestamps
- meeting_attendee: Join table for the many-to-many relationship

## Key Features
- Webhook API for ingesting meeting data
- Unique attendee tracking across meetings 
- Company domain visualization and statistics
- Meeting filtering by domain or individual attendee
- Interactive charts with clickable elements
- YAML generation for meeting data export

## Frontend
- Jinja2 templates with Bootstrap styling
- Simple UI for meeting list and YAML generation
- Client-side JavaScript for interactive features

## Environmental Setup
- Database connection requires DATABASE_URL and DIRECT_URL in .env file
- Uses python-dotenv for environment configuration
- PostgreSQL database with psycopg2 driver

## Testing
- test_webhook.py provides simulated webhook payloads
- No automated testing framework implemented yet