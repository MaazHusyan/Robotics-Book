from abc import ABC, abstractmethod
from typing import List, Optional
from src.embedding.models.embedding_models import EmbeddingVector, EmbeddingConfig
from src.embedding.models.content_models import ContentChunk


class EmbeddingServiceInterface(ABC):
    """
    Abstract interface for embedding services.
    """

    @abstractmethod
    def generate_embedding(self, text: str, model: Optional[str] = None) -> EmbeddingVector:
        """
        Generate a single embedding for the given text.

        Args:
            text: Text to embed
            model: Model to use (uses default if not provided)

        Returns:
            EmbeddingVector containing the generated embedding
        """
        pass

    @abstractmethod
    def generate_embeddings_batch(self, texts: List[str], model: Optional[str] = None) -> List[EmbeddingVector]:
        """
        Generate embeddings for a batch of texts.

        Args:
            texts: List of texts to embed
            model: Model to use (uses default if not provided)

        Returns:
            List of EmbeddingVector objects
        """
        pass

    @abstractmethod
    def process_content_chunk(self, chunk: ContentChunk, model: Optional[str] = None) -> EmbeddingVector:
        """
        Process a single content chunk and generate its embedding.

        Args:
            chunk: Content chunk to process
            model: Model to use (uses default if not provided)

        Returns:
            EmbeddingVector containing the generated embedding
        """
        pass

    @abstractmethod
    def process_content_batch(self, chunks: List[ContentChunk], model: Optional[str] = None) -> List[EmbeddingVector]:
        """
        Process a batch of content chunks and generate their embeddings.

        Args:
            chunks: List of content chunks to process
            model: Model to use (uses default if not provided)

        Returns:
            List of EmbeddingVector objects
        """
        pass