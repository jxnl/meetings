# Test Suite for Meetings App

This document provides instructions for setting up and running the test suite for the Meetings App.

## Setup

1. Install the required testing dependencies:

```bash
pip install -r test-requirements.txt
```

## Running Tests

### Running All Tests

To run all tests:

```bash
pytest
```

### Running Specific Test Files

To run specific test files:

```bash
# Run webhook API tests
pytest tests/api/test_webhooks.py

# Run meetings API tests
pytest tests/api/test_meetings.py

# Run service tests
pytest tests/services/test_meeting_service.py
```

### Running with Verbosity

For more detailed output:

```bash
pytest -v
```

### Running with Coverage Report

To generate a test coverage report:

```bash
# Install pytest-cov first
pip install pytest-cov

# Run with coverage
pytest --cov=app tests/
```

## Test Structure

- `tests/conftest.py`: Contains shared test fixtures
- `tests/api/`: Contains API endpoint tests
- `tests/services/`: Contains service function tests

## Adding New Tests

When adding new features to the application, make sure to:

1. Create corresponding test cases
2. Follow the existing test structure
3. Use fixtures from `conftest.py` where appropriate
4. Consider edge cases and error conditions

## Mocked Dependencies

The test suite uses:

- SQLite in-memory database instead of PostgreSQL
- Mocked background tasks
- HTML parsing with BeautifulSoup for template-based responses

## Test Database

The tests use an in-memory SQLite database that is created fresh for each test. This ensures:

1. Tests are isolated from each other
2. No impact on development or production databases
3. Fast test execution without external dependencies