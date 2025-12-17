import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from backend.src.utils.embedding_storage import FileBasedEmbeddingStorage
from backend.src.embedding.models.embedding_models import EmbeddingVector


class TestFileBasedEmbeddingStorage:
    """Test class for file-based embedding storage functionality."""

    def test_save_and_load_single_embedding(self):
        """Test saving and loading a single embedding."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = FileBasedEmbeddingStorage(temp_dir)

            # Create a test embedding
            embedding = EmbeddingVector(
                chunk_id="test-chunk-1",
                vector=[0.1, 0.2, 0.3, 0.4],
                model="test-model",
                dimensionality=4
            )

            # Save the embedding
            filepath = storage.save_embedding(embedding)

            # Verify the file was created
            assert os.path.exists(filepath)

            # Load the embedding back
            loaded_embedding = storage.load_embedding(filepath)

            # Verify the loaded embedding matches the original
            assert loaded_embedding is not None
            assert loaded_embedding.chunk_id == embedding.chunk_id
            assert loaded_embedding.vector == embedding.vector
            assert loaded_embedding.model == embedding.model
            assert loaded_embedding.dimensionality == embedding.dimensionality

    def test_save_embeddings_batch(self):
        """Test saving a batch of embeddings."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = FileBasedEmbeddingStorage(temp_dir)

            # Create test embeddings
            embeddings = [
                EmbeddingVector(
                    chunk_id=f"test-chunk-{i}",
                    vector=[float(i), float(i+1), float(i+2)],
                    model="test-model",
                    dimensionality=3
                )
                for i in range(3)
            ]

            # Save the embeddings batch
            filepaths = storage.save_embeddings_batch(embeddings)

            # Verify all files were created
            assert len(filepaths) == 3
            for filepath in filepaths:
                assert os.path.exists(filepath)

    def test_load_all_embeddings(self):
        """Test loading all embeddings from storage."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = FileBasedEmbeddingStorage(temp_dir)

            # Create and save test embeddings
            embeddings = [
                EmbeddingVector(
                    chunk_id=f"test-chunk-{i}",
                    vector=[float(i), float(i+1)],
                    model="test-model",
                    dimensionality=2
                )
                for i in range(2)
            ]

            storage.save_embeddings_batch(embeddings)

            # Load all embeddings
            all_embeddings = storage.load_all_embeddings()

            # Verify all embeddings were loaded by checking that we have the right chunk_ids
            assert len(all_embeddings) == 2
            loaded_chunk_ids = {emb.chunk_id for emb in all_embeddings}
            expected_chunk_ids = {f"test-chunk-{i}" for i in range(2)}
            assert loaded_chunk_ids == expected_chunk_ids

            # Verify all embeddings have the correct dimensionality
            for loaded_embedding in all_embeddings:
                assert loaded_embedding.dimensionality == 2

    def test_delete_embedding(self):
        """Test deleting an embedding file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = FileBasedEmbeddingStorage(temp_dir)

            # Create and save a test embedding
            embedding = EmbeddingVector(
                chunk_id="test-chunk-delete",
                vector=[0.5, 0.6],
                model="test-model",
                dimensionality=2
            )

            filepath = storage.save_embedding(embedding)
            assert os.path.exists(filepath)

            # Delete the embedding
            result = storage.delete_embedding(filepath)
            assert result is True
            assert not os.path.exists(filepath)

    def test_get_embedding_file_path(self):
        """Test getting embedding file path by chunk_id."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = FileBasedEmbeddingStorage(temp_dir)

            # Create and save a test embedding
            embedding = EmbeddingVector(
                chunk_id="specific-chunk-id",
                vector=[0.7, 0.8],
                model="test-model",
                dimensionality=2
            )

            filepath = storage.save_embedding(embedding)

            # Get the file path by chunk_id
            retrieved_path = storage.get_embedding_file_path("specific-chunk-id")

            # Verify the path matches
            assert retrieved_path is not None
            assert "specific-chunk-id" in retrieved_path
            assert os.path.basename(retrieved_path) == os.path.basename(filepath)

    def test_load_nonexistent_embedding(self):
        """Test loading a non-existent embedding file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = FileBasedEmbeddingStorage(temp_dir)

            # Try to load a non-existent file
            result = storage.load_embedding("/nonexistent/path.json")

            # Should return None
            assert result is None

    def test_get_nonexistent_embedding_file_path(self):
        """Test getting file path for non-existent chunk_id."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = FileBasedEmbeddingStorage(temp_dir)

            # Try to get path for non-existent chunk_id
            result = storage.get_embedding_file_path("nonexistent-id")

            # Should return None
            assert result is None