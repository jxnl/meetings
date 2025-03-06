# Test Suite for Meetings App

## Setup

1. Install test dependencies:

```bash
pip install -r test-requirements.txt
```

## Running Tests

Run all tests:

```bash
pytest
```

Run specific tests:

```bash
# Run webhook API tests
pytest tests/test_webhook_api.py

# Run meetings API tests
pytest tests/test_meetings_api.py

# Run service tests
pytest tests/test_meeting_service.py
```

Run with verbose output:

```bash
pytest -v
```

Run with coverage report:

```bash
pip install pytest-cov
pytest --cov=app
```

## Test Structure

- `conftest.py`: Shared fixtures for tests
- `test_webhook_api.py`: Tests for webhook API endpoints
- `test_meetings_api.py`: Tests for meetings API endpoints
- `test_meeting_service.py`: Tests for meeting service functions

## Test Database

Tests use an in-memory SQLite database that resets between tests.