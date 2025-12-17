import asyncio
import cohere
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


class CohereEmbeddingService:
    """
    Service for generating embeddings using Cohere's API.
    """

    def __init__(self, config: Optional[EmbeddingConfig] = None, storage_type: str = "qdrant", storage_dir: str = "embeddings_storage", collection_name: str = "robotics_embeddings"):
        """
        Initialize the Cohere embedding service.

        Args:
            config: Embedding configuration (uses defaults if not provided)
            storage_type: Type of storage to use ("file" or "qdrant") - default is "qdrant"
            storage_dir: Directory to store embeddings (for file-based storage)
            collection_name: Name of the Qdrant collection (for Qdrant storage)
        """
        self.config = config or EmbeddingConfig()
        self.api_key = getattr(settings, 'COHERE_API_KEY', None)

        if not self.api_key:
            raise ValueError("COHERE_API_KEY environment variable is required")

        self.client = cohere.Client(self.api_key)
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
        if len(text) > 10000:  # Rough check for token count
            raise ContentTooLongError(len(text), 4000)

        # Wait for rate limit if needed
        self.rate_limiter.wait_if_needed()

        try:
            response = self.client.embed(
                texts=[text],
                model=model or self.config.model,
                input_type=self.config.input_type,
                truncate=self.config.truncate
            )

            if not response.embeddings or len(response.embeddings) == 0:
                raise EmbeddingGenerationError("No embeddings returned from Cohere API")

            embedding_vector = response.embeddings[0]
            dimensionality = len(embedding_vector)

            return EmbeddingVector(
                chunk_id="",  # Will be set by the caller
                vector=embedding_vector,
                model=model or self.config.model,
                dimensionality=dimensionality
            )
        except cohere.errors.BadRequestError as e:
            raise CohereAPIError(f"Bad Request Error from Cohere API: {str(e)}", 400)
        except cohere.errors.UnauthorizedError as e:
            raise CohereAPIError(f"Unauthorized Error from Cohere API: {str(e)}", 401)
        except cohere.errors.ForbiddenError as e:
            raise CohereAPIError(f"Forbidden Error from Cohere API: {str(e)}", 403)
        except cohere.errors.TooManyRequestsError as e:
            raise CohereAPIError(f"Rate Limit Error from Cohere API: {str(e)}", 429)
        except cohere.errors.InternalServerError as e:
            raise CohereAPIError(f"Internal Server Error from Cohere API: {str(e)}", 500)
        except cohere.errors.ServiceUnavailableError as e:
            raise CohereAPIError(f"Service Unavailable Error from Cohere API: {str(e)}", 503)
        except Exception as e:
            # Re-raise EmbeddingGenerationError to preserve explicit errors
            if isinstance(e, EmbeddingGenerationError):
                raise
            # Catch other general exceptions
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
            if len(text) > 10000:  # Rough check for token count
                raise ContentTooLongError(len(text), 4000)

        # Wait for rate limit if needed
        self.rate_limiter.wait_if_needed()

        try:
            response = self.client.embed(
                texts=texts,
                model=model or self.config.model,
                input_type=self.config.input_type,
                truncate=self.config.truncate
            )

            if not response.embeddings or len(response.embeddings) != len(texts):
                raise EmbeddingGenerationError("Mismatch between input texts and returned embeddings")

            embedding_vectors = []
            for i, embedding in enumerate(response.embeddings):
                dimensionality = len(embedding)
                embedding_vector = EmbeddingVector(
                    chunk_id="",  # Will be set by the caller
                    vector=embedding,
                    model=model or self.config.model,
                    dimensionality=dimensionality
                )
                embedding_vectors.append(embedding_vector)

            return embedding_vectors
        except cohere.errors.BadRequestError as e:
            raise CohereAPIError(f"Bad Request Error from Cohere API: {str(e)}", 400)
        except cohere.errors.UnauthorizedError as e:
            raise CohereAPIError(f"Unauthorized Error from Cohere API: {str(e)}", 401)
        except cohere.errors.ForbiddenError as e:
            raise CohereAPIError(f"Forbidden Error from Cohere API: {str(e)}", 403)
        except cohere.errors.TooManyRequestsError as e:
            raise CohereAPIError(f"Rate Limit Error from Cohere API: {str(e)}", 429)
        except cohere.errors.InternalServerError as e:
            raise CohereAPIError(f"Internal Server Error from Cohere API: {str(e)}", 500)
        except cohere.errors.ServiceUnavailableError as e:
            raise CohereAPIError(f"Service Unavailable Error from Cohere API: {str(e)}", 503)
        except Exception as e:
            # Re-raise EmbeddingGenerationError to preserve explicit errors
            if isinstance(e, EmbeddingGenerationError):
                raise
            # Catch other general exceptions
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

                # Set chunk IDs and store embeddings
                for j, embedding in enumerate(batch_embeddings):
                    embedding.chunk_id = batch[j].id
                    self.storage.save_embedding(embedding)  # Store each embedding
                    all_embeddings.append(embedding)

            return all_embeddings
        else:
            # Process as a single batch
            texts = [chunk.text for chunk in chunks]
            embeddings = self.generate_embeddings_batch(texts, model)

            # Set chunk IDs and store embeddings
            for i, embedding in enumerate(embeddings):
                embedding.chunk_id = chunks[i].id
                self.storage.save_embedding(embedding)  # Store each embedding

            return embeddings