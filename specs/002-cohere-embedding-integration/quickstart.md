# Quickstart: Cohere Embedding Integration for Robotics Book

## Prerequisites
- Python 3.11+
- pip package manager
- Cohere API key

## Setup

1. Create a virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

2. Install dependencies:
```bash
pip install cohere python-dotenv
```

3. Add Cohere API key to your `.env` file:
```
COHERE_API_KEY=your-cohere-api-key-here
```

## Running the Embedding Service

1. Set up your book content in the appropriate directory structure
2. Run the embedding script:
```bash
python -c "
import sys
sys.path.append('.')
from backend.src.embedding.services.cohere_service import CohereEmbeddingService
from backend.src.config import settings

# Initialize the service
service = CohereEmbeddingService(settings)

# Process your book content
# service.process_content_batch('path/to/book/content')
"
```

## Basic Usage Flow

1. Prepare your book content in text format
2. Initialize the Cohere embedding service
3. Process content in batches respecting API limits
4. Store generated embeddings for later retrieval

## Example API Requests (when API endpoints are implemented)

```bash
# Trigger embedding generation for book content
curl -X POST http://localhost:8000/api/v1/embeddings/generate \
  -H "Content-Type: application/json" \
  -d '{
    "content_path": "/path/to/book/content",
    "model": "embed-english-v3.0",
    "input_type": "search_document"
  }'

# Check embedding job status
curl http://localhost:8000/api/v1/embeddings/job/{job_id}

# Get similarity between content chunks
curl -X POST http://localhost:8000/api/v1/embeddings/similarity \
  -H "Content-Type: application/json" \
  -d '{
    "vector1": [0.1, 0.2, 0.3],
    "vector2": [0.4, 0.5, 0.6]
  }'
```

## Configuration

Create a `.env` file with the following variables:

```
# Cohere Configuration
COHERE_API_KEY=your-api-key-here

# Embedding Configuration
EMBEDDING_MODEL=embed-english-v3.0
EMBEDDING_INPUT_TYPE=search_document
EMBEDDING_TRUNCATE=END
EMBEDDING_BATCH_SIZE=96
EMBEDDING_RATE_LIMIT_REQUESTS=100
EMBEDDING_RATE_LIMIT_SECONDS=60
EMBEDDING_RETRY_ATTEMPTS=3
```

## Environment Variables

Required:
- `COHERE_API_KEY`: Your Cohere API key for authentication

Optional:
- `EMBEDDING_MODEL`: Cohere embedding model to use (default: embed-english-v3.0)
- `EMBEDDING_INPUT_TYPE`: Type of input for embeddings (default: search_document)
- `EMBEDDING_BATCH_SIZE`: Number of chunks to process per API call (default: 96)
- `EMBEDDING_RATE_LIMIT_REQUESTS`: Max API requests per time window (default: 100)
- `EMBEDDING_RATE_LIMIT_SECONDS`: Time window in seconds for rate limiting (default: 60)
- `EMBEDDING_RETRY_ATTEMPTS`: Number of retry attempts for failed API calls (default: 3)