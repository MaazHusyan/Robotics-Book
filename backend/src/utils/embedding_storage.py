import json
import os
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime
import sys

# Add the src directory to the path for relative imports
src_path = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, src_path)

from src.embedding.models.embedding_models import EmbeddingVector
from src.utils.storage_interface import EmbeddingStorageInterface


class FileBasedEmbeddingStorage(EmbeddingStorageInterface):
    """
    Temporary file-based storage for embedding vectors.
    This is a temporary solution until a proper database or vector store is implemented.
    """

    def __init__(self, storage_dir: str = "embeddings_storage"):
        """
        Initialize the file-based embedding storage.

        Args:
            storage_dir: Directory to store embedding files
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)

    def save_embedding(self, embedding: EmbeddingVector) -> str:
        """
        Save a single embedding vector to a file.

        Args:
            embedding: The embedding vector to save

        Returns:
            The file path where the embedding was saved
        """
        # Create a filename based on the chunk_id and timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"embedding_{embedding.chunk_id}_{timestamp}.json"
        filepath = self.storage_dir / filename

        # Prepare the embedding data for storage
        embedding_data = {
            "chunk_id": embedding.chunk_id,
            "vector": embedding.vector,
            "model": embedding.model,
            "dimensionality": embedding.dimensionality,
            "created_at": datetime.now().isoformat()
        }

        # Write the embedding data to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(embedding_data, f, indent=2)

        return str(filepath)

    def save_embeddings_batch(self, embeddings: List[EmbeddingVector]) -> List[str]:
        """
        Save a batch of embedding vectors to files.

        Args:
            embeddings: List of embedding vectors to save

        Returns:
            List of file paths where embeddings were saved
        """
        filepaths = []
        for embedding in embeddings:
            filepath = self.save_embedding(embedding)
            filepaths.append(filepath)
        return filepaths

    def load_embedding(self, filepath: str) -> Optional[EmbeddingVector]:
        """
        Load a single embedding vector from a file.

        Args:
            filepath: Path to the embedding file

        Returns:
            The loaded embedding vector or None if file doesn't exist
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                embedding_data = json.load(f)

            return EmbeddingVector(
                chunk_id=embedding_data["chunk_id"],
                vector=embedding_data["vector"],
                model=embedding_data["model"],
                dimensionality=embedding_data["dimensionality"]
            )
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            return None

    def load_all_embeddings(self) -> List[EmbeddingVector]:
        """
        Load all embedding vectors from the storage directory.

        Returns:
            List of all embedding vectors in the storage
        """
        embeddings = []
        for filepath in self.storage_dir.glob("*.json"):
            embedding = self.load_embedding(str(filepath))
            if embedding:
                embeddings.append(embedding)
        return embeddings

    def delete_embedding(self, filepath: str) -> bool:
        """
        Delete an embedding file.

        Args:
            filepath: Path to the embedding file to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            os.remove(filepath)
            return True
        except (FileNotFoundError, OSError):
            return False

    def load_all_embeddings(self) -> List[EmbeddingVector]:
        """
        Load all embedding vectors from the storage directory.

        Returns:
            List of all embedding vectors in the storage
        """
        embeddings = []
        for filepath in self.storage_dir.glob("*.json"):
            embedding = self.load_embedding(str(filepath))
            if embedding:
                embeddings.append(embedding)
        return embeddings

    def get_embedding_file_path(self, chunk_id: str) -> Optional[str]:
        """
        Get the file path for an embedding with the given chunk_id.

        Args:
            chunk_id: The chunk ID to search for

        Returns:
            The file path if found, None otherwise
        """
        for filepath in self.storage_dir.glob(f"*{chunk_id}*.json"):
            return str(filepath)
        return None