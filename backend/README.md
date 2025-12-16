# Robotics Book API

This is a FastAPI-based API service for accessing robotics book content. It provides programmatic access to book content with health monitoring, configuration management, and automatic documentation.

## Features

- RESTful API endpoints for accessing robotics book content
- Health and status monitoring endpoints
- Configuration management with environment variables
- CORS support
- Automatic API documentation with Swagger UI and ReDoc
- Request logging middleware
- Comprehensive test suite

## Prerequisites

- Python 3.11+
- pip package manager

## Installation

1. Clone the repository
2. Navigate to the backend directory
3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Create a `.env` file in the backend directory with the following variables:

```
# Server Configuration
ENVIRONMENT=development
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true
LOG_LEVEL=info

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,https://yourdomain.com
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=*
CORS_ALLOW_HEADERS=*

# Additional Configuration
DATABASE_URL=sqlite:///./robotics_book.db
MAX_REQUEST_SIZE=10MB
```

## Running the Application

### Development

```bash
uvicorn main:app --reload
```

### Production

```bash
# Using uvicorn with production settings
uvicorn main:app --host 0.0.0.0 --port 8000

# Or using a process manager like gunicorn (install separately)
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## API Endpoints

- `GET /` - Root endpoint with API information
- `GET /api/v1/book/content` - Get book content by chapter and section
- `GET /api/v1/book/chapter/{chapter}` - Get all content for a specific chapter
- `GET /api/v1/book/search` - Search for content containing a query string
- `GET /api/v1/book/all` - Get all book content
- `GET /api/v1/health` - Health check endpoint
- `GET /api/v1/ready` - Readiness check endpoint
- `GET /api/v1/status` - Status information endpoint
- `GET /api/v1/metrics` - API metrics endpoint

API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

Run the tests with:

```bash
python -m pytest
```

To run tests with coverage:

```bash
pip install coverage
coverage run -m pytest
coverage report
```

## Environment Variables

- `ENVIRONMENT`: Application environment (default: "development")
- `API_HOST`: Host address for the API server (default: "0.0.0.0")
- `API_PORT`: Port for the API server (default: 8000)
- `DEBUG`: Enable debug mode (default: "true")
- `LOG_LEVEL`: Logging level (default: "info")
- `ALLOWED_ORIGINS`: Comma-separated list of allowed origins (default: "*")
- `CORS_ALLOW_CREDENTIALS`: Allow credentials in CORS requests (default: "true")
- `CORS_ALLOW_METHODS`: Allowed HTTP methods (default: "*")
- `CORS_ALLOW_HEADERS`: Allowed headers (default: "*")
- `DATABASE_URL`: Database connection string (optional)
- `MAX_REQUEST_SIZE`: Maximum request size (default: "10MB")

## Docker Deployment

To build and run with Docker:

```Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t robotics-book-api .
docker run -p 8000:8000 --env-file .env robotics-book-api
```

## Architecture

The application follows a clean architecture pattern:

- `api/` - FastAPI route handlers
- `models/` - Pydantic data models
- `services/` - Business logic
- `utils/` - Utility functions and middleware
- `tests/` - Unit and integration tests

## Error Handling

The API includes comprehensive error handling with appropriate HTTP status codes and meaningful error messages. Custom exceptions are defined in `src/exceptions.py`.

## Logging

The application uses structured logging with configurable log levels. All requests are logged with processing time information.

## Next Steps

This API serves as the foundation for future functionality including embedding, retrieval, and chatbot integration. The architecture is designed to be extensible for additional features.