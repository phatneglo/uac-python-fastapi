# UAC Python FastAPI

A modern authentication system built with FastAPI, PostgreSQL, and JWT tokens.

## Features

- User registration and login
- JWT-based authentication
- Password hashing with bcrypt
- Email validation
- Protected endpoints
- Login with username or email
- OAuth2 form login support
- Comprehensive error handling
- Health check endpoint

## Requirements

- Python 3.11+
- PostgreSQL database
- Dependencies listed in `requirements.txt`

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd uac-python-fastapi
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the root directory:
```env
DATABASE_URL=postgresql+asyncpg://postgres:0yq5h3to9@localhost/base_uac
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=True
```

4. Set up the database:
Make sure PostgreSQL is running and the `base_uac` database exists with the required tables.

## Running the Application

Start the FastAPI server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- Main API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## API Endpoints

### Authentication

- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Login with username/email and password
- `POST /api/v1/auth/login/form` - OAuth2 form login
- `GET /api/v1/auth/me` - Get current user info (protected)

### Health Check

- `GET /health` - Health check endpoint

## Testing

The project includes comprehensive integration tests organized by feature:

### Run All Tests
```bash
pytest
```

### Run Specific Test Types
```bash
# Authentication tests only
pytest -m auth

# Health endpoint tests
pytest tests/test_health.py

# Integration tests
pytest -m integration

# Slow tests
pytest -m slow
```

### Using the Test Runner Script
```bash
# Run all tests
python run_tests.py

# Run specific test types
python run_tests.py --type auth
python run_tests.py --type health
python run_tests.py --type integration

# Run with verbose output
python run_tests.py --type auth -v

# Run with coverage report
python run_tests.py --coverage

# Run specific test file
python run_tests.py --file test_auth_endpoints.py
```

### Test Structure
```
tests/
├── __init__.py
├── conftest.py                 # Shared fixtures and configuration
├── test_health.py             # Health endpoint tests
├── test_auth_endpoints.py     # Authentication endpoint tests (with fixtures)
└── test_auth_integration.py   # Complete authentication flow tests
```

**Note**: Make sure the FastAPI server is running on `http://localhost:8000` before running tests.

## Project Structure

```
app/
├── __init__.py
├── main.py              # FastAPI app with lifespan
├── config.py            # Settings with pydantic
├── dependencies.py      # Shared dependencies
├── database.py          # Database setup
├── models/              # SQLAlchemy models
│   ├── __init__.py
│   └── user.py
├── schemas/             # Pydantic models
│   ├── __init__.py
│   └── user.py
├── routers/             # APIRouter modules
│   ├── __init__.py
│   └── auth.py
├── services/            # Business logic
│   ├── __init__.py
│   └── user_service.py
└── utils/               # Utilities
    ├── __init__.py
    └── security.py
```

## Usage Examples

### Register a new user
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "testuser",
       "email": "test@example.com",
       "password": "testpass123",
       "first_name": "Test",
       "last_name": "User"
     }'
```

### Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "testuser",
       "password": "testpass123"
     }'
```

### Access protected endpoint
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Security Features

- Passwords are hashed using bcrypt
- JWT tokens with configurable expiration
- Protected endpoints require valid JWT tokens
- Input validation with Pydantic
- SQL injection protection with SQLAlchemy

## Development

The project follows FastAPI best practices:
- Async/await for I/O operations
- Dependency injection for database sessions
- Proper error handling and HTTP status codes
- Type hints throughout
- Pydantic models for request/response validation

## License

This project is licensed under the MIT License. 