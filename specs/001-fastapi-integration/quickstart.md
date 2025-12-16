# Quickstart: FastAPI Integration for Robotics Book

## Prerequisites
- Python 3.11+
- pip package manager

## Configuration Options

The application can be configured using environment variables. Create a `.env` file in the backend directory or set environment variables directly:

### Required Configuration
- `ENVIRONMENT`: Application environment (default: "development")
- `API_HOST`: Host address for the API server (default: "0.0.0.0")
- `API_PORT`: Port for the API server (default: 8000)
- `DEBUG`: Enable debug mode (default: "true")
- `LOG_LEVEL`: Logging level (default: "info")

### CORS Configuration
- `ALLOWED_ORIGINS`: Comma-separated list of allowed origins (default: "*")
- `CORS_ALLOW_CREDENTIALS`: Allow credentials in CORS requests (default: "true")
- `CORS_ALLOW_METHODS`: Allowed HTTP methods (default: "*")
- `CORS_ALLOW_HEADERS`: Allowed headers (default: "*")

### Additional Configuration
- `DATABASE_URL`: Database connection string (optional)
- `MAX_REQUEST_SIZE`: Maximum request size (default: "10MB")

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

2. Install dependencies:
```bash
pip install fastapi uvicorn python-dotenv pydantic pytest
```

3. Create environment file:
```bash
touch .env
```

4. Add configuration to `.env`:
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
```

## Running the Service

1. Start the API server:
```bash
uvicorn main:app --reload
```

2. Access the API:
   - API Root: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/api/v1/health
   - Status: http://localhost:8000/api/v1/status

## Basic Usage Flow

1. Start the FastAPI server
2. Access the auto-generated API documentation at /docs
3. Test the health endpoint at /api/v1/health
4. Access book content through /api/v1/book/content endpoint

## Example API Requests

```bash
# Check API health
curl http://localhost:8000/api/v1/health

# Get book content
curl "http://localhost:8000/api/v1/book/content?chapter=1&section=1.1"

# Get API status
curl http://localhost:8000/api/v1/status

# Get API metrics
curl http://localhost:8000/api/v1/metrics
```

## Environment Variables

Create a `.env` file with the following variables:

```
# Server Configuration
ENVIRONMENT=development
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false
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