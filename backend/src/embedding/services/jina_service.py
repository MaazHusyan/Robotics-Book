import asyncio
import requests
from typing import List, Optional
import sys
import os

# Add the parent directory to the path so we can import from config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from config import settings

# Add the src directory to the path for relative imports
src_path = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, src_path)

from src.embedding.models.embedding_models import EmbeddingVector, EmbeddingConfig
from src.embedding.models.content_models import ContentChunk
from src.embedding.exceptions import CohereAPIError, ContentTooLongError, EmbeddingGenerationError
from src.utils.rate_limiter import CohereRateLimiter
from src.utils.similarity_calculator import cosine_similarity
from src.utils.storage_interface import EmbeddingStorageInterface
from src.utils.embedding_storage import FileBasedEmbeddingStorage
from src.utils.qdrant_storage import QdrantEmbeddingStorage
from src.embedding.services.embedding_service_interface import EmbeddingServiceInterface


class JinaEmbeddingService(EmbeddingServiceInterface):
    """
    Service for generating embeddings using Jina AI's API.
    """

    def __init__(self, config: Optional[EmbeddingConfig] = None, storage_type: str = "qdrant", storage_dir: str = "embeddings_storage", collection_name: str = "robotics_embeddings"):
        """
        Initialize the Jina embedding service.

        Args:
            config: Embedding configuration (uses defaults if not provided)
            storage_type: Type of storage to use ("file" or "qdrant") - default is "qdrant"
            storage_dir: Directory to store embeddings (for file-based storage)
            collection_name: Name of the Qdrant collection (for Qdrant storage)
        """
        self.config = config or EmbeddingConfig()
        self.api_key = getattr(settings, 'JINA_API_KEY', None)

        if not self.api_key:
            raise ValueError("JINA_API_KEY environment variable is required")

        self.base_url = "https://api.jina.ai/v1"
        self.rate_limiter = CohereRateLimiter(
            max_requests=self.config.rate_limit_requests,
            time_window_seconds=self.config.rate_limit_seconds
        )

        # Initialize storage based on type
        if storage_type.lower() == "qdrant":
            self.storage = QdrantEmbeddingStorage(collection_name=collection_name)
        else:
            self.storage = FileBasedEmbeddingStorage(storage_dir)

    def generate_embedding(self, text: str, model: Optional[str] = None) -> EmbeddingVector:
        """
        Generate a single embedding for the given text.

        Args:
            text: Text to embed
            model: Model to use (uses default if not provided)

        Returns:
            EmbeddingVector containing the generated embedding
        """
        # Validate input length
        if len(text) > 8192:  # Jina AI has an 8192 character limit
            raise ContentTooLongError(len(text), 8192)

        # Wait for rate limit if needed
        self.rate_limiter.wait_if_needed()

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model or self.config.model,
            "input": [text],
            "task": "retrieval.query"  # Using retrieval.query for search_document equivalent
        }

        try:
            response = requests.post(f"{self.base_url}/embeddings", headers=headers, json=payload)

            if response.status_code != 200:
                raise EmbeddingGenerationError(f"Jina API error: {response.status_code} - {response.text}")

            result = response.json()

            if not result.get("data") or len(result["data"]) == 0:
                raise EmbeddingGenerationError("No embeddings returned from Jina API")

            embedding_data = result["data"][0]
            embedding_vector = embedding_data["embedding"]
            dimensionality = len(embedding_vector)

            return EmbeddingVector(
                chunk_id="",  # Will be set by the caller
                vector=embedding_vector,
                model=model or self.config.model,
                dimensionality=dimensionality
            )
        except requests.exceptions.RequestException as e:
            raise EmbeddingGenerationError(f"Network error during Jina API call: {str(e)}")
        except KeyError as e:
            raise EmbeddingGenerationError(f"Missing expected field in Jina API response: {str(e)}")
        except Exception as e:
            raise EmbeddingGenerationError(f"Failed to generate embedding: {str(e)}")

    def generate_embeddings_batch(self, texts: List[str], model: Optional[str] = None) -> List[EmbeddingVector]:
        """
        Generate embeddings for a batch of texts.

        Args:
            texts: List of texts to embed
            model: Model to use (uses default if not provided)

        Returns:
            List of EmbeddingVector objects
        """
        if len(texts) > self.config.batch_size:
            raise ValueError(f"Batch size {len(texts)} exceeds maximum allowed size {self.config.batch_size}")

        # Validate input lengths
        for i, text in enumerate(texts):
            if len(text) > 8192:  # Jina AI has an 8192 character limit
                raise ContentTooLongError(len(text), 8192)

        # Wait for rate limit if needed
        self.rate_limiter.wait_if_needed()

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model or self.config.model,
            "input": texts,
            "task": "retrieval.document"  # Using retrieval.document for search_document equivalent
        }

        try:
            response = requests.post(f"{self.base_url}/embeddings", headers=headers, json=payload)

            if response.status_code != 200:
                raise EmbeddingGenerationError(f"Jina API error: {response.status_code} - {response.text}")

            result = response.json()

            if not result.get("data") or len(result["data"]) != len(texts):
                raise EmbeddingGenerationError("Mismatch between input texts and returned embeddings")

            embedding_vectors = []
            for i, embedding_data in enumerate(result["data"]):
                embedding = embedding_data["embedding"]
                dimensionality = len(embedding)
                embedding_vector = EmbeddingVector(
                    chunk_id="",  # Will be set by the caller
                    vector=embedding,
                    model=model or self.config.model,
                    dimensionality=dimensionality
                )
                embedding_vectors.append(embedding_vector)

            return embedding_vectors
        except requests.exceptions.RequestException as e:
            raise EmbeddingGenerationError(f"Network error during Jina API call: {str(e)}")
        except KeyError as e:
            raise EmbeddingGenerationError(f"Missing expected field in Jina API response: {str(e)}")
        except Exception as e:
            raise EmbeddingGenerationError(f"Failed to generate embeddings: {str(e)}")

    def process_content_chunk(self, chunk: ContentChunk, model: Optional[str] = None) -> EmbeddingVector:
        """
        Process a single content chunk and generate its embedding.

        Args:
            chunk: Content chunk to process
            model: Model to use (uses default if not provided)

        Returns:
            EmbeddingVector containing the generated embedding
        """
        embedding = self.generate_embedding(chunk.text, model)
        embedding.chunk_id = chunk.id
        # Transfer metadata from content chunk to embedding vector
        embedding.metadata = {
            "source_file": chunk.source_file,
            "source_location": chunk.source_location,
            **chunk.metadata  # Include any additional metadata from the chunk
        }
        # Store the embedding in the file-based storage
        self.storage.save_embedding(embedding)
        return embedding

    def process_content_batch(self, chunks: List[ContentChunk], model: Optional[str] = None) -> List[EmbeddingVector]:
        """
        Process a batch of content chunks and generate their embeddings.

        Args:
            chunks: List of content chunks to process
            model: Model to use (uses default if not provided)

        Returns:
            List of EmbeddingVector objects
        """
        if len(chunks) > self.config.batch_size:
            # Process in smaller batches if needed
            all_embeddings = []
            for i in range(0, len(chunks), self.config.batch_size):
                batch = chunks[i:i + self.config.batch_size]
                texts = [chunk.text for chunk in batch]
                batch_embeddings = self.generate_embeddings_batch(texts, model)

                # Set chunk IDs and metadata, then store embeddings
                for j, embedding in enumerate(batch_embeddings):
                    embedding.chunk_id = batch[j].id
                    # Transfer metadata from content chunk to embedding vector
                    embedding.metadata = {
                        "source_file": batch[j].source_file,
                        "source_location": batch[j].source_location,
                        **batch[j].metadata  # Include any additional metadata from the chunk
                    }
                    self.storage.save_embedding(embedding)  # Store each embedding
                    all_embeddings.append(embedding)

            return all_embeddings
        else:
            # Process as a single batch
            texts = [chunk.text for chunk in chunks]
            embeddings = self.generate_embeddings_batch(texts, model)

            # Set chunk IDs and metadata, then store embeddings
            for i, embedding in enumerate(embeddings):
                embedding.chunk_id = chunks[i].id
                # Transfer metadata from content chunk to embedding vector
                embedding.metadata = {
                    "source_file": chunks[i].source_file,
                    "source_location": chunks[i].source_location,
                    **chunks[i].metadata  # Include any additional metadata from the chunk
                }
                self.storage.save_embedding(embedding)  # Store each embedding

            return embeddings