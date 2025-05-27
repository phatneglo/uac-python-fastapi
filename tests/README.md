# Tests Directory

This directory contains all tests for the UAC FastAPI project, organized by feature and test type.

## Test Organization

### 📁 File Structure

```
tests/
├── __init__.py                 # Makes tests a Python package
├── conftest.py                 # Shared pytest fixtures and configuration
├── test_health.py             # Health endpoint tests
├── test_auth_endpoints.py     # Authentication endpoint tests (using fixtures)
├── test_auth_integration.py   # Complete authentication flow tests
└── README.md                  # This file
```

### 🏷️ Test Markers

Tests are organized using pytest markers:

- `@pytest.mark.integration` - Integration tests that require a running server
- `@pytest.mark.auth` - Authentication-related tests
- `@pytest.mark.slow` - Tests that take longer to run

### 🔧 Fixtures (conftest.py)

Shared fixtures available to all tests:

- `base_url` - Base URL for the FastAPI server
- `api_client` - HTTP client for making API requests
- `unique_timestamp` - Unique timestamp for test data
- `test_user_data` - Generated test user data
- `registered_user` - Pre-registered test user
- `authenticated_user` - Logged-in test user with token
- `auth_headers` - Authorization headers for protected endpoints

## Test Files

### test_health.py
- Tests for health check endpoints
- Validates response format and status
- Quick smoke tests

### test_auth_endpoints.py
- Focused authentication endpoint tests
- Uses pytest fixtures for clean test setup
- Organized into test classes by functionality:
  - `TestAuthRegistration` - User registration tests
  - `TestAuthLogin` - User login tests
  - `TestProtectedEndpoints` - Protected endpoint tests
  - `TestCompleteAuthFlow` - End-to-end authentication flows

### test_auth_integration.py
- Complete authentication integration tests
- Tests full user journeys
- Self-contained tests (no fixtures)
- Comprehensive error case coverage

## Running Tests

### All Tests
```bash
pytest tests/
```

### Specific Test Files
```bash
pytest tests/test_health.py
pytest tests/test_auth_endpoints.py
pytest tests/test_auth_integration.py
```

### By Markers
```bash
pytest -m auth          # Authentication tests only
pytest -m integration   # Integration tests only
pytest -m slow          # Slow tests only
```

### With Verbose Output
```bash
pytest tests/ -v
```

### Specific Test Classes or Methods
```bash
pytest tests/test_auth_endpoints.py::TestAuthRegistration
pytest tests/test_auth_endpoints.py::TestAuthRegistration::test_user_registration_success
```

## Test Data Strategy

- **Unique Identifiers**: All test data uses timestamps to ensure uniqueness
- **Isolation**: Each test is independent and doesn't rely on other tests
- **Cleanup**: Tests don't require manual cleanup (data is unique per run)
- **Fixtures**: Reusable test data and setup through pytest fixtures

## Adding New Tests

### For New Features
1. Create a new test file: `test_<feature_name>.py`
2. Add appropriate markers (`@pytest.mark.integration`, etc.)
3. Use existing fixtures or create new ones in `conftest.py`
4. Follow the naming convention: `test_<action>_<expected_result>`

### For New Authentication Features
- Add to `test_auth_endpoints.py` if using fixtures
- Add to `test_auth_integration.py` if testing complete flows
- Use the `@pytest.mark.auth` marker

### Example New Test
```python
@pytest.mark.integration
@pytest.mark.auth
def test_new_auth_feature(self, api_client, authenticated_user, auth_headers):
    """Test description."""
    response = api_client.get("/api/v1/auth/new-feature", headers=auth_headers)
    assert response.status_code == 200
```

## Best Practices

1. **Descriptive Names**: Test names should clearly describe what is being tested
2. **Single Responsibility**: Each test should test one specific behavior
3. **Arrange-Act-Assert**: Structure tests with clear setup, action, and verification
4. **Use Fixtures**: Leverage pytest fixtures for common setup
5. **Mark Tests**: Use appropriate markers for test organization
6. **Document**: Add docstrings to test classes and complex tests

## Prerequisites

- FastAPI server running on `http://localhost:8000`
- PostgreSQL database with required tables
- All dependencies installed (`pip install -r requirements.txt`)

## Troubleshooting

### Server Not Running
If tests fail with connection errors, ensure the FastAPI server is running:
```bash
uvicorn app.main:app --reload
```

### Database Issues
If tests fail with database errors, check:
- PostgreSQL is running
- Database `base_uac` exists
- Required tables are created
- Database credentials are correct in `.env`

### Fixture Issues
If fixture-related errors occur:
- Check `conftest.py` for fixture definitions
- Ensure fixtures are properly scoped
- Verify fixture dependencies are available 