# Testing Plan for Meetings API

## Test Requirements

We need to install pytest and some additional packages for API testing:

```
pytest
pytest-asyncio  # For testing async endpoints
httpx           # HTTP client for FastAPI testing
pytest-mock     # For mocking dependencies
```

## API Components to Test

1. **Webhook API** (`app/api/routes/webhooks.py`):
   - `POST /api/webhooks/` - Receives meeting data
   - `GET /api/webhooks/{meeting_id}` - Gets a meeting by ID
   - `GET /api/webhooks/` - Lists all meetings
   - `DELETE /api/webhooks/{meeting_id}` - Deletes a meeting

2. **Meetings API** (`app/api/routes/meetings/route.py`):
   - `GET /api/meetings/` - HTML list of meetings
   - `GET /api/meetings/domains` - List attendees by company domains
   - `POST /api/meetings/generate-yaml` - Generate YAML for selected meetings
   - `GET /api/meetings/analytics` - Display meeting analytics dashboard
   - `GET /api/meetings/organizations` - List organizations based on email domains
   - `POST /api/meetings/action-items/{action_item_id}/update` - Update action item status

## Test Structure

### 1. Fixtures

- Database session fixture using SQLAlchemy in-memory SQLite
- FastAPI test client fixture
- Meeting factory fixture for test data generation
- Mock background task fixture

### 2. Test Files Organization

- `tests/conftest.py` - Shared fixtures
- `tests/api/test_webhooks.py` - Tests for webhook endpoints
- `tests/api/test_meetings.py` - Tests for meetings endpoints
- `tests/services/test_meeting_service.py` - Tests for meeting service functions

## Test Cases

### Webhook API Tests

1. **POST /api/webhooks/**
   - Test successful creation of meeting
   - Test creation with minimal data
   - Test duplicate external ID (should return 409)
   - Test invalid payload format (should return 422)
   - Test database error handling (mock DB error, should return 500)

2. **GET /api/webhooks/{meeting_id}**
   - Test successful retrieval of existing meeting
   - Test non-existent meeting ID (should return 404)

3. **GET /api/webhooks/**
   - Test listing meetings with default pagination
   - Test listing with custom pagination (skip, limit)
   - Test empty result list

4. **DELETE /api/webhooks/{meeting_id}**
   - Test successful deletion of meeting
   - Test deleting non-existent meeting (should return 404)

### Meetings API Tests

1. **GET /api/meetings/**
   - Test listing all meetings (HTML response)
   - Test filtering by domain
   - Test filtering by email

2. **GET /api/meetings/domains**
   - Test listing domains (HTML response)
   - Test with empty database

3. **POST /api/meetings/generate-yaml**
   - Test generating YAML from selected meetings
   - Test with non-existent meeting IDs
   - Test with empty selection

4. **GET /api/meetings/analytics**
   - Test general analytics view
   - Test with time period filter
   - Test user-specific analytics

5. **GET /api/meetings/organizations**
   - Test listing organizations
   - Test with empty database

6. **POST /api/meetings/action-items/{action_item_id}/update**
   - Test successful status update
   - Test with non-existent action item ID

## Implementation Plan

1. Set up testing infrastructure:
   - Create basic test directory structure
   - Configure pytest
   - Implement database fixtures

2. Implement service layer tests first
   - Test core service functions used by APIs

3. Implement webhook API tests
   - Focus on data processing and validation

4. Implement meetings API tests
   - Focus on view rendering and filtering

## Testing the HTML Responses

For the endpoints that return HTML:
- Test the status code
- Check for key elements in the HTML response
- Verify the correct template is used
- Check that expected context variables are passed to templates

## Mocking vs. Integration Testing

- Use mocking for database session and background tasks
- Use actual template rendering for HTML response tests
- Consider creating a subset of DB schema in SQLite for integration tests