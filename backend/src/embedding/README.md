# Embedding Service

This module provides functionality to generate vector embeddings for robotics book content using various embedding APIs (Cohere, Jina AI, etc.). The embeddings enable semantic search and retrieval for the chatbot.

## Components

### Services

- `CohereEmbeddingService`: Service for generating embeddings using Cohere's API
  - Handles single and batch embedding generation
  - Implements rate limiting to respect API quotas
  - Provides comprehensive error handling
  - Stores embeddings using file-based storage

- `JinaEmbeddingService`: Service for generating embeddings using Jina AI's API
  - Handles single and batch embedding generation
  - Implements rate limiting to respect API quotas
  - Provides comprehensive error handling
  - Stores embeddings using file-based storage

- `EmbeddingServiceFactory`: Factory for creating the appropriate embedding service based on configuration
  - Automatically selects service based on the configured model name
  - Supports switching between Cohere, Jina, and other embedding providers
  - Provides a unified interface for all embedding operations

### Models

- `EmbeddingVector`: Represents a vector embedding with metadata
- `EmbeddingConfig`: Configuration for embedding generation
- `ContentChunk`: Represents a chunk of content to be embedded
- `EmbeddingJob`: Represents an embedding job (for batch processing)

### Utilities

- `FileBasedEmbeddingStorage`: Temporary file-based storage for embeddings
- `CohereRateLimiter`: Rate limiting functionality for API calls
- `similarity_calculator`: Functions for calculating similarity between embeddings

### Exceptions

- Custom exception classes for different error scenarios

## Usage

### Single Content Processing

```python
from backend.src.embedding.services.embedding_service_factory import EmbeddingServiceFactory
from backend.src.embedding.models.content_models import ContentChunk

# Initialize the service using the factory (automatically selects based on config)
service = EmbeddingServiceFactory.create_embedding_service()

# Create a content chunk
chunk = ContentChunk(
    id="chunk-1",
    text="This is robotics content to embed",
    source_file="robotics_book.pdf",
    source_location="page_10"
)

# Process the chunk and generate embedding
embedding = service.process_content_chunk(chunk)
```

### Batch Content Processing

```python
# Process multiple chunks at once
chunks = [chunk1, chunk2, chunk3]
embeddings = service.process_content_batch(chunks)
```

## Storage

Embeddings are stored in a temporary file-based storage system in the `embeddings_storage` directory. Each embedding is saved as a JSON file with the format:

```json
{
  "chunk_id": "unique_chunk_id",
  "vector": [0.1, 0.2, 0.3, ...],
  "model": "embed-multilingual-v2.0",
  "dimensionality": 1024,
  "created_at": "2023-12-16T10:30:00.123456"
}
```

## Configuration

The service can be configured using environment variables in the `.env` file:

- `COHERE_API_KEY`: Your Cohere API key (required if using Cohere models)
- `JINA_API_KEY`: Your Jina AI API key (required if using Jina models)
- `EMBEDDING_MODEL`: The embedding model to use (default: jina-embeddings-v3)
- `EMBEDDING_BATCH_SIZE`: Maximum batch size for API calls (default: 32 for Jina, 96 for Cohere)
- `RATE_LIMIT_REQUESTS`: Max requests per time window (default: 10)
- `RATE_LIMIT_SECONDS`: Time window in seconds (default: 60)

The system automatically selects the appropriate service based on the EMBEDDING_MODEL setting:
- If the model name contains "jina", the JinaEmbeddingService is used
- Otherwise, the CohereEmbeddingService is used (for backward compatibility)