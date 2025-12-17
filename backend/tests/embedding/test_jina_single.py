import pytest
from unittest.mock import Mock, patch
from backend.src.embedding.services.jina_service import JinaEmbeddingService
from backend.src.embedding.models.content_models import ContentChunk
from backend.src.embedding.models.embedding_models import EmbeddingVector, EmbeddingConfig
from backend.src.embedding.exceptions import CohereAPIError, ContentTooLongError, EmbeddingGenerationError


class TestJinaEmbeddingServiceSingle:
    """Test class for Jina Embedding Service single embedding functionality."""

    @pytest.fixture
    def mock_config(self):
        """Fixture to create a mock embedding configuration."""
        config = EmbeddingConfig()
        config.model = "jina-embeddings-v3"
        config.input_type = "retrieval.query"
        config.truncate = "END"
        config.rate_limit_requests = 10
        config.rate_limit_seconds = 60
        config.batch_size = 32
        return config

    @pytest.fixture
    def mock_content_chunk(self):
        """Fixture to create a mock content chunk."""
        return ContentChunk(
            id="test-chunk-1",
            text="This is a sample robotics book content for testing.",
            source_file="test_book.pdf",
            source_location="page_15",
            metadata={"chapter": "1", "section": "1.1"}
        )

    def test_generate_embedding_success(self, mock_config, mock_content_chunk):
        """Test successful generation of a single embedding."""
        # Mock the requests.post and settings
        with patch('backend.src.embedding.services.jina_service.requests.post') as mock_post, \
             patch('backend.src.embedding.services.jina_service.settings') as mock_settings:

            # Set up mock settings to return a fake API key
            mock_settings.JINA_API_KEY = "fake-api-key-for-testing"

            # Create service instance
            service = JinaEmbeddingService(config=mock_config)

            # Mock the Jina API response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "data": [
                    {"embedding": [0.1, 0.2, 0.3, 0.4, 0.5]}
                ]
            }
            mock_post.return_value = mock_response

            # Generate embedding
            result = service.generate_embedding(mock_content_chunk.text)

            # Verify the result
            assert isinstance(result, EmbeddingVector)
            assert result.vector == [0.1, 0.2, 0.3, 0.4, 0.5]
            assert result.dimensionality == 5
            assert result.model == mock_config.model

            # Verify API call
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args[0][0] == "https://api.jina.ai/v1/embeddings"
            assert "Authorization" in call_args[1]["headers"]
            assert call_args[1]["json"]["model"] == mock_config.model
            assert call_args[1]["json"]["input"] == [mock_content_chunk.text]

    def test_generate_embedding_with_custom_model(self, mock_config, mock_content_chunk):
        """Test generating embedding with a custom model."""
        custom_model = "jina-embeddings-v2"

        # Mock the requests.post and settings
        with patch('backend.src.embedding.services.jina_service.requests.post') as mock_post, \
             patch('backend.src.embedding.services.jina_service.settings') as mock_settings:

            # Set up mock settings to return a fake API key
            mock_settings.JINA_API_KEY = "fake-api-key-for-testing"

            # Create service instance
            service = JinaEmbeddingService(config=mock_config)

            # Mock the Jina API response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "data": [
                    {"embedding": [0.5, 0.4, 0.3, 0.2, 0.1]}
                ]
            }
            mock_post.return_value = mock_response

            # Generate embedding with custom model
            result = service.generate_embedding(mock_content_chunk.text, model=custom_model)

            # Verify the result
            assert result.vector == [0.5, 0.4, 0.3, 0.2, 0.1]
            assert result.model == custom_model

            # Verify API call used the custom model
            call_args = mock_post.call_args
            assert call_args[1]["json"]["model"] == custom_model

    def test_generate_embedding_api_error(self, mock_config, mock_content_chunk):
        """Test handling of API errors during embedding generation."""
        # Mock the requests.post to return an error
        with patch('backend.src.embedding.services.jina_service.requests.post') as mock_post, \
             patch('backend.src.embedding.services.jina_service.settings') as mock_settings:

            # Set up mock settings to return a fake API key
            mock_settings.JINA_API_KEY = "fake-api-key-for-testing"

            # Create service instance
            service = JinaEmbeddingService(config=mock_config)

            # Mock the Jina API response to return an error
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.text = "Bad Request"
            mock_post.return_value = mock_response

            # Expect an exception
            with pytest.raises(EmbeddingGenerationError) as exc_info:
                service.generate_embedding(mock_content_chunk.text)

            # Verify the exception message
            assert "Jina API error: 400" in str(exc_info.value)

    def test_generate_embedding_network_error(self, mock_config, mock_content_chunk):
        """Test handling of network errors during embedding generation."""
        # Mock the requests.post to raise an exception
        with patch('backend.src.embedding.services.jina_service.requests.post') as mock_post, \
             patch('backend.src.embedding.services.jina_service.settings') as mock_settings:

            # Set up mock settings to return a fake API key
            mock_settings.JINA_API_KEY = "fake-api-key-for-testing"

            # Create service instance
            service = JinaEmbeddingService(config=mock_config)

            # Mock the Jina API to raise a network error
            mock_post.side_effect = Exception("Network error")

            # Expect an exception
            with pytest.raises(EmbeddingGenerationError) as exc_info:
                service.generate_embedding(mock_content_chunk.text)

            # Verify the exception message
            assert "Network error" in str(exc_info.value)

    def test_generate_embedding_content_too_long(self, mock_config, mock_content_chunk):
        """Test handling of content that exceeds the length limit."""
        # Create content that exceeds the 8192 character limit
        long_text = "x" * 9000  # More than 8192 characters

        # Create service instance
        service = JinaEmbeddingService(config=mock_config)

        # Expect an exception
        with pytest.raises(ContentTooLongError) as exc_info:
            service.generate_embedding(long_text)

        # Verify the exception
        assert exc_info.value.length == 9000
        assert exc_info.value.max_length == 8192

    def test_process_content_chunk(self, mock_config, mock_content_chunk):
        """Test processing a content chunk with the service."""
        # Mock the requests.post and settings
        with patch('backend.src.embedding.services.jina_service.requests.post') as mock_post, \
             patch('backend.src.embedding.services.jina_service.settings') as mock_settings:

            # Set up mock settings to return a fake API key
            mock_settings.JINA_API_KEY = "fake-api-key-for-testing"

            # Create service instance with file storage
            import tempfile
            with tempfile.TemporaryDirectory() as temp_dir:
                service = JinaEmbeddingService(config=mock_config, storage_type="file", storage_dir=temp_dir)

                # Mock the Jina API response
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "data": [
                        {"embedding": [0.1, 0.2, 0.3]}
                    ]
                }
                mock_post.return_value = mock_response

                # Process the content chunk
                result = service.process_content_chunk(mock_content_chunk)

                # Verify the result
                assert result.chunk_id == mock_content_chunk.id
                assert result.vector == [0.1, 0.2, 0.3]
                assert result.dimensionality == 3

                # Verify the embedding was stored
                stored_embeddings = service.storage.load_all_embeddings()
                assert len(stored_embeddings) == 1
                stored_embedding = stored_embeddings[0]
                assert stored_embedding.chunk_id == mock_content_chunk.id