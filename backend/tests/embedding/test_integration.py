import pytest
import tempfile
from unittest.mock import Mock, patch
from backend.src.embedding.services.cohere_service import CohereEmbeddingService
from backend.src.embedding.models.content_models import ContentChunk
from backend.src.embedding.models.embedding_models import EmbeddingConfig


class TestCohereIntegration:
    """Integration tests for Cohere service with storage functionality."""

    @pytest.fixture
    def mock_config(self):
        """Fixture to create a mock embedding configuration."""
        config = EmbeddingConfig()
        config.model = "embed-multilingual-v2.0"
        config.input_type = "search_document"
        config.truncate = "END"
        config.rate_limit_requests = 10
        config.rate_limit_seconds = 60
        config.batch_size = 96
        return config

    def test_process_content_chunk_with_storage(self, mock_config):
        """Test processing a content chunk with storage integration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock both the Cohere client and settings
            with patch('backend.src.embedding.services.cohere_service.cohere.Client'), \
                 patch('backend.src.embedding.services.cohere_service.settings') as mock_settings:

                # Set up mock settings to return a fake API key
                mock_settings.COHERE_API_KEY = "fake-api-key-for-testing"

                # Create service with custom storage directory and file storage type
                service = CohereEmbeddingService(config=mock_config, storage_type="file", storage_dir=temp_dir)

                # Mock the Cohere client response
                mock_response = Mock()
                mock_response.embeddings = [[0.1, 0.2, 0.3, 0.4]]
                service.client.embed.return_value = mock_response

                # Create a content chunk
                chunk = ContentChunk(
                    id="test-chunk-integration",
                    text="This is a test content chunk for integration testing.",
                    source_file="test_source.txt",
                    source_location="page_1",
                    metadata={"test": True}
                )

                # Process the content chunk
                result = service.process_content_chunk(chunk)

                # Verify the result
                assert result.chunk_id == chunk.id
                assert result.vector == [0.1, 0.2, 0.3, 0.4]
                assert result.dimensionality == 4

                # Verify that the embedding was stored
                stored_embeddings = service.storage.load_all_embeddings()
                assert len(stored_embeddings) == 1
                stored_embedding = stored_embeddings[0]
                assert stored_embedding.chunk_id == chunk.id
                assert stored_embedding.vector == [0.1, 0.2, 0.3, 0.4]

    def test_process_content_batch_with_storage(self, mock_config):
        """Test processing a content batch with storage integration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock both the Cohere client and settings
            with patch('backend.src.embedding.services.cohere_service.cohere.Client'), \
                 patch('backend.src.embedding.services.cohere_service.settings') as mock_settings:

                # Set up mock settings to return a fake API key
                mock_settings.COHERE_API_KEY = "fake-api-key-for-testing"

                # Create service with custom storage directory and file storage type
                service = CohereEmbeddingService(config=mock_config, storage_type="file", storage_dir=temp_dir)

                # Mock the Cohere client response for batch
                mock_response = Mock()
                mock_response.embeddings = [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]
                service.client.embed.return_value = mock_response

                # Create content chunks
                chunks = [
                    ContentChunk(
                        id=f"test-chunk-batch-{i}",
                        text=f"This is test content {i} for batch processing.",
                        source_file="test_source.txt",
                        source_location=f"page_{i}",
                        metadata={"batch_test": True}
                    )
                    for i in range(3)
                ]

                # Process the content batch
                results = service.process_content_batch(chunks)

                # Verify the results
                assert len(results) == 3
                expected_vectors = [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]
                for i, result in enumerate(results):
                    assert result.chunk_id == chunks[i].id
                    assert result.vector == expected_vectors[i]
                    assert result.dimensionality == 2

                # Verify that all embeddings were stored
                stored_embeddings = service.storage.load_all_embeddings()
                assert len(stored_embeddings) == 3

                # Verify each stored embedding
                stored_chunk_ids = {emb.chunk_id for emb in stored_embeddings}
                expected_chunk_ids = {f"test-chunk-batch-{i}" for i in range(3)}
                assert stored_chunk_ids == expected_chunk_ids