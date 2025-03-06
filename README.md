# FastAPI Application

A simple FastAPI application with a clean architecture for processing meeting data from webhooks.

## Features

- FastAPI framework with automatic OpenAPI documentation
- SQLAlchemy ORM for database operations
- Pydantic for data validation
- Clean architecture with separation of concerns
- RESTful API endpoints
- Supabase PostgreSQL integration
- Webhook endpoint for receiving meeting data
- Meeting data processing and storage

## Project Structure

```
.
├── app
│   ├── api
│   │   ├── routes
│   │   │   ├── __init__.py
│   │   │   ├── items.py
│   │   │   └── webhooks.py
│   │   └── __init__.py
│   ├── core
│   │   ├── __init__.py
│   │   ├── app.py
│   │   └── config.py
│   ├── db
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── base_class.py
│   │   └── session.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── item.py
│   │   └── meeting.py
│   ├── schemas
│   │   ├── __init__.py
│   │   ├── item.py
│   │   └── meeting.py
│   ├── services
│   │   ├── __init__.py
│   │   ├── item_service.py
│   │   └── meeting_service.py
│   ├── static
│   ├── templates
│   └── __init__.py
├── .env
├── main.py
├── README.md
└── requirements.txt
```

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   uv pip install -r requirements.txt
   ```
4. Set up your `.env` file with database credentials:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/dbname
   DIRECT_URL=postgresql://user:password@localhost:5432/dbname
   ```
5. Run the application:
   ```
   uvicorn main:app --reload
   ```

## API Documentation

Once the application is running, you can access the API documentation at:

- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Webhook Endpoint

The application provides a webhook endpoint for receiving meeting data:

- **URL**: `/api/webhooks/`
- **Method**: POST
- **Payload**: JSON meeting data (see example below)

Example webhook payload:
```json
{
  "id": 123,
  "name": "Team Meeting",
  "createdAt": "2023-06-15T14:00:00Z",
  "duration": 3600,
  "url": "https://example.com/meeting/123",
  "attendees": [
    {
      "name": "John Doe",
      "email": "john@example.com"
    },
    {
      "name": "Jane Smith",
      "email": "jane@example.com"
    }
  ],
  "recordingUrl": "https://example.com/recording/123",
  "notes": "Meeting notes in markdown format",
  "actionItems": [
    {
      "title": "Research new feature",
      "description": "Look into implementing the new feature",
      "assignee_name": "John Doe",
      "assignee_email": "john@example.com"
    }
  ]
}
```

## Database Migrations

To set up database migrations with Alembic:

1. Initialize Alembic:
   ```
   alembic init alembic
   ```

2. Edit `alembic/env.py` to import your models and set up the database URL:
   ```python
   from app.db.base import Base
   from app.core.config import settings
   
   # ... existing code ...
   
   config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
   target_metadata = Base.metadata
   ```

3. Create a migration:
   ```
   alembic revision --autogenerate -m "Initial migration"
   ```

4. Apply the migration:
   ```
   alembic upgrade head
   ```

## Development

To add a new feature:

1. Create a new model in `app/models/`
2. Create corresponding schemas in `app/schemas/`
3. Create a service in `app/services/`
4. Create API routes in `app/api/routes/`
5. Include the new router in `app/api/routes/__init__.py` 