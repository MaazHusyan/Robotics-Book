# Quickstart Guide: RAG Chatbot Implementation

**Date**: 2025-12-14  
**Feature**: RAG Chatbot Integration  
**Purpose**: Development setup and deployment guide for RAG chatbot implementation

## Prerequisites

### Required Accounts & Services
- **Neon Database**: Serverless Postgres instance (free tier)
  - Sign up at https://neon.tech
  - Save connection string: `NEON_DATABASE_URL`
- **Qdrant Cloud**: Vector database (free tier)
  - Sign up at https://cloud.qdrant.tech
  - Save API key: `QDRANT_API_KEY`
  - Save cluster URL: `QDRANT_URL`
- **Google Gemini API**: LLM integration
  - Get API key from Google AI Studio
  - Save API key: `GEMINI_API_KEY`
  - Set custom base URL for Gemini compatibility

### Development Environment
- **Python**: 3.9+ with pip package management
- **Node.js**: 18+ with npm package management
- **Git**: For version control and collaboration
- **VS Code**: Recommended IDE with extensions for Python/TypeScript

## Project Setup

### 1. Repository Setup
```bash
# Clone repository (if not already done)
git clone https://github.com/your-org/robotics-book.git
cd robotics-book

# Switch to feature branch
git checkout 001-rag-chatbot

# Install dependencies
pip install -r backend/requirements.txt
npm install
```

### 2. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your actual values:
NEON_DATABASE_URL=postgresql://user:password@ep-xxx-xxx.us-east-1.aws.neon.tech/dbname?sslmode=require
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_URL=https://xxx-xxx.aws.cloud.qdrant.tech:6333
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Database Setup
```bash
# Run database migrations
cd backend
python -m alembic upgrade head

# Verify database connection
python -c "
from app.services.neon import get_db_connection
db = get_db_connection()
print('Database connection successful!')
"
```

### 4. Qdrant Collection Setup
```bash
# Initialize Qdrant collection
cd backend
python scripts/setup_qdrant.py

# Verify collection creation
curl -X "API-Key: $QDRANT_API_KEY" \
     "$QDRANT_URL/collections/robotics_book_embeddings"
```

### 5. Content Ingestion
```bash
# Ingest existing book content
cd backend
python scripts/ingest_content.py

# Verify ingestion
python -c "
from app.services.neon import get_db_connection
from app.services.qdrant import get_qdrant_client
db = get_db_connection()
qdrant = get_qdrant_client()
count = db.execute('SELECT COUNT(*) FROM books_content').scalar()
print(f'Ingested {count} content sections')
"
```

## Development Workflow

### Backend Development (FastAPI)

```bash
# Start development server
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest tests/ -v

# Check API documentation
open http://localhost:8000/docs
```

### Frontend Development (React + Docusaurus)

```bash
# Start Docusaurus development server
cd frontend
npm run start

# Access chatbot interface
open http://localhost:3000
```

### API Testing

```bash
# Test health endpoint
curl http://localhost:8000/api/health

# Create session
curl -X POST http://localhost:8000/api/sessions \
     -H "Content-Type: application/json" \
     -d '{"user_identifier": "test_user"}'

# Ask question
curl -X POST http://localhost:8000/api/chat/ask \
     -H "Content-Type: application/json" \
     -d '{
       "session_id": "your-session-id",
       "query": "What is Zero Moment Point?"
     }'
```

## Project Structure

### Backend Files
```
backend/
├── app/
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── chat.py          # Chat question/answer
│   │   │   ├── sessions.py       # Session management
│   │   │   ├── health.py         # Health checks
│   │   │   └── ingestion.py      # Content ingestion
│   ├── models/
│   │   ├── database.py         # SQLAlchemy models
│   │   ├── schemas.py          # Pydantic models
│   │   └── embeddings.py       # Vector operations
│   ├── services/
│   │   ├── rag.py             # RAG orchestration
│   │   ├── gemini.py          # Gemini API
│   │   ├── qdrant.py          # Vector database
│   │   └── neon.py            # Postgres operations
│   └── main.py                 # FastAPI app
├── tests/
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   └── performance/            # Performance tests
├── scripts/
│   ├── ingest_content.py        # Content ingestion
│   └── setup_qdrant.py         # Qdrant setup
└── requirements.txt               # Python dependencies
```

### Frontend Files
```
frontend/src/components/rag-chatbot/
├── ChatInterface.tsx          # Main chat UI
├── TextSelector.tsx           # Text selection
├── SourceCitation.tsx        # Source display
└── ConversationHistory.tsx     # History management

frontend/styles/
└── chatbot.module.css          # Chatbot styling

frontend/lib/
└── api.ts                    # API client functions
```

## Configuration

### Backend Configuration
```python
# app/main.py - FastAPI settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="RAG Chatbot API",
    description="API for robotics book RAG chatbot",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-org.github.io"],
    allow_credentials=True,
)
```

### Frontend Configuration
```javascript
// frontend/lib/api.ts - API client configuration
const API_BASE_URL = process.env.NODE_ENV === 'development' 
    ? 'http://localhost:8000' 
    : 'https://api.robotics-book.com';

export const chatbotConfig = {
    apiBaseUrl: API_BASE_URL,
    maxRetries: 3,
    timeout: 30000, // 30 seconds
    retryDelay: 1000, // 1 second
};
```

## Testing Strategy

### Backend Tests
```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# Performance tests
pytest tests/performance/ -v

# Coverage report
pytest --cov=app tests/ -v
```

### Frontend Tests
```bash
# React component tests
npm test -- --coverage

# End-to-end tests
npm run test:e2e

# Linting
npm run lint
npm run type-check
```

## Deployment

### Backend Deployment
```bash
# Deploy to serverless platform (Vercel, Railway, etc.)
vercel --prod

# Environment variables for production
NEON_DATABASE_URL=postgresql://user:password@ep-xxx-xxx.us-east-1.aws.neon.tech/dbname?sslmode=require
QDRANT_API_KEY=prod_qdrant_key
QDRANT_URL=https://xxx-xxx.aws.cloud.qdrant.tech:6333
GEMINI_API_KEY=prod_gemini_key
```

### Frontend Deployment
```bash
# Deploy to GitHub Pages
npm run build

# Deploy to GitHub Pages
npm run deploy

# Docusaurus configuration update
# Update docusaurus.config.js with chatbot plugin
```

## Monitoring & Debugging

### Backend Monitoring
```python
# Logging configuration
import logging
logging.basicConfig(level=logging.INFO)

# Performance monitoring
import time
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

### Frontend Monitoring
```javascript
// Error boundaries for React components
import { ErrorBoundary } from 'react';

// Performance monitoring
const startTime = performance.now();
// ... API call
const endTime = performance.now();
console.log(`API call took ${endTime - startTime}ms`);
```

## Troubleshooting

### Common Issues
1. **Database Connection**: Check NEON_DATABASE_URL format
2. **Qdrant Connection**: Verify API key and cluster URL
3. **CORS Errors**: Ensure frontend URL in allowed origins
4. **Gemini API**: Check API key and rate limits
5. **Content Ingestion**: Verify MDX file paths and parsing

### Debug Commands
```bash
# Backend debugging
python -m pdb app/main.py

# Frontend debugging
npm run start:debug
```

## Next Steps

1. **Complete Implementation**: Follow the plan.md structure
2. **Testing**: Run comprehensive test suite
3. **Documentation**: Update API docs as needed
4. **Deployment**: Deploy to production environment
5. **Monitoring**: Set up logging and performance monitoring

## Support

- **Documentation**: `/specs/001-rag-chatbot/` directory
- **API Reference**: http://localhost:8000/docs (development)
- **Issues**: Create GitHub issues for bugs and feature requests
- **Community**: Join discussions for questions and contributions