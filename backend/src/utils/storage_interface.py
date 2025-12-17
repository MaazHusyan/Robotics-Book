from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import sys
import os

# Add the src directory to the path for relative imports
src_path = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, src_path)

from src.embedding.models.embedding_models import EmbeddingVector


class EmbeddingStorageInterface(ABC):
    """
    Abstract interface for embedding storage systems.
    This allows switching between different storage backends (file-based, Qdrant, etc.)
    """

    @abstractmethod
    def save_embedding(self, embedding: EmbeddingVector) -> str:
        """
        Save a single embedding vector.

        Args:
            embedding: The embedding vector to save

        Returns:
            The ID of the stored embedding
        """
        pass

    @abstractmethod
    def save_embeddings_batch(self, embeddings: List[EmbeddingVector]) -> List[str]:
        """
        Save a batch of embedding vectors.

        Args:
            embeddings: List of embedding vectors to save

        Returns:
            List of IDs of the stored embeddings
        """
        pass

    @abstractmethod
    def load_embedding(self, identifier: str) -> Optional[EmbeddingVector]:
        """
        Load a single embedding vector.

        Args:
            identifier: The identifier of the embedding to load

        Returns:
            The loaded embedding vector or None if not found
        """
        pass

    @abstractmethod
    def load_all_embeddings(self) -> List[EmbeddingVector]:
        """
        Load all embedding vectors from storage.

        Returns:
            List of all embedding vectors in storage
        """
        pass

    @abstractmethod
    def delete_embedding(self, identifier: str) -> bool:
        """
        Delete an embedding from storage.

        Args:
            identifier: The identifier of the embedding to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        pass