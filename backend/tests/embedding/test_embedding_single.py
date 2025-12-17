import pytest
from unittest.mock import Mock, patch
from backend.src.embedding.services.cohere_service import CohereEmbeddingService
from backend.src.embedding.models.content_models import ContentChunk
from backend.src.embedding.models.embedding_models import EmbeddingVector, EmbeddingConfig
from backend.src.embedding.exceptions import CohereAPIError, ContentTooLongError, EmbeddingGenerationError


class TestCohereEmbeddingServiceSingle:
    """Test class for Cohere Embedding Service single embedding functionality."""

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

    @pytest.fixture
    def mock_content_chunk(self):
        """Fixture to create a mock content chunk."""
        return ContentChunk(
            id="test-chunk-1",
            text="This is a sample robotics book content for testing.",
            source_file="test_book.pdf",
            source_location="page_10",
            metadata={"chapter": "Introduction", "section": "1.1"}
        )

    @pytest.fixture
    def cohere_service(self, mock_config):
        """Fixture to create a Cohere embedding service instance."""
        # Mock both the Cohere client and settings to avoid actual API calls and API key requirement
        with patch('backend.src.embedding.services.cohere_service.cohere.Client'), \
             patch('backend.src.embedding.services.cohere_service.settings') as mock_settings:
            # Set up mock settings to return a fake API key
            mock_settings.COHRE_API_KEY = "fake-api-key-for-testing"
            mock_settings.COHERE_API_KEY = "fake-api-key-for-testing"
            service = CohereEmbeddingService(config=mock_config)
            return service

    def test_generate_single_embedding_success(self, cohere_service, mock_content_chunk):
        """Test successful generation of a single embedding."""
        # Mock the Cohere client response
        mock_response = Mock()
        mock_response.embeddings = [[0.1, 0.2, 0.3, 0.4]]
        cohere_service.client.embed.return_value = mock_response

        # Generate embedding
        result = cohere_service.process_content_chunk(mock_content_chunk)

        # Assertions
        assert isinstance(result, EmbeddingVector)
        assert result.chunk_id == mock_content_chunk.id
        assert result.vector == [0.1, 0.2, 0.3, 0.4]
        assert result.model == cohere_service.config.model
        assert result.dimensionality == 4
        cohere_service.client.embed.assert_called_once()

    def test_generate_single_embedding_with_custom_model(self, cohere_service, mock_content_chunk):
        """Test successful generation of a single embedding with custom model."""
        custom_model = "custom-embed-model"
        mock_response = Mock()
        mock_response.embeddings = [[0.5, 0.6, 0.7]]
        cohere_service.client.embed.return_value = mock_response

        # Generate embedding with custom model
        result = cohere_service.process_content_chunk(mock_content_chunk, model=custom_model)

        # Assertions
        assert result.model == custom_model
        assert result.vector == [0.5, 0.6, 0.7]
        assert result.dimensionality == 3

        # Verify the custom model was passed to the API call
        cohere_service.client.embed.assert_called_once_with(
            texts=[mock_content_chunk.text],
            model=custom_model,
            input_type=cohere_service.config.input_type,
            truncate=cohere_service.config.truncate
        )

    def test_generate_single_embedding_from_text(self, cohere_service):
        """Test successful generation of a single embedding from raw text."""
        test_text = "This is a test sentence for embedding."
        mock_response = Mock()
        mock_response.embeddings = [[0.1, 0.2, 0.3]]
        cohere_service.client.embed.return_value = mock_response

        # Generate embedding from text
        result = cohere_service.generate_embedding(test_text)

        # Assertions
        assert isinstance(result, EmbeddingVector)
        assert result.vector == [0.1, 0.2, 0.3]
        assert result.dimensionality == 3
        cohere_service.client.embed.assert_called_once()

    def test_generate_single_embedding_content_too_long(self, cohere_service):
        """Test that ContentTooLongError is raised for content exceeding limits."""
        # Create content longer than 10000 characters
        long_text = "x" * 10001

        with pytest.raises(ContentTooLongError):
            cohere_service.generate_embedding(long_text)

    def test_generate_single_embedding_cohere_api_error(self, cohere_service):
        """Test that CohereAPIError is raised when Cohere API returns an error."""
        from backend.src.embedding.exceptions import CohereAPIError
        import cohere.errors

        # Mock Cohere client to raise an error
        cohere_service.client.embed.side_effect = cohere.errors.TooManyRequestsError("Rate limit exceeded")

        with pytest.raises(CohereAPIError):
            cohere_service.generate_embedding("test text")

    def test_generate_single_embedding_general_error(self, cohere_service):
        """Test that EmbeddingGenerationError is raised for general errors."""
        # Mock Cohere client to raise a general exception
        cohere_service.client.embed.side_effect = Exception("General error")

        with pytest.raises(EmbeddingGenerationError):
            cohere_service.generate_embedding("test text")

    def test_generate_single_embedding_empty_response(self, cohere_service):
        """Test that EmbeddingGenerationError is raised when API returns no embeddings."""
        # Mock response with empty embeddings
        mock_response = Mock()
        mock_response.embeddings = []
        cohere_service.client.embed.return_value = mock_response

        with pytest.raises(EmbeddingGenerationError):
            cohere_service.generate_embedding("test text")

    def test_rate_limiter_called_for_single_embedding(self, cohere_service):
        """Test that rate limiter is called when generating a single embedding."""
        test_text = "This is a test sentence."
        mock_response = Mock()
        mock_response.embeddings = [[0.1, 0.2, 0.3]]
        cohere_service.client.embed.return_value = mock_response

        # Mock the rate limiter
        with patch.object(cohere_service.rate_limiter, 'wait_if_needed') as mock_wait:
            cohere_service.generate_embedding(test_text)

            # Verify that rate limiter was called
            mock_wait.assert_called_once()

    def test_embedding_dimensionality_consistency(self, cohere_service, mock_content_chunk):
        """Test that embedding dimensionality is correctly calculated."""
        # Test with different dimensionalities
        test_cases = [
            ([0.1], 1),
            ([0.1, 0.2], 2),
            ([0.1, 0.2, 0.3, 0.4, 0.5], 5),
            (list(range(100)), 100)  # Large embedding vector
        ]

        for vector, expected_dim in test_cases:
            mock_response = Mock()
            mock_response.embeddings = [vector]
            cohere_service.client.embed.return_value = mock_response

            result = cohere_service.process_content_chunk(mock_content_chunk)

            assert result.dimensionality == expected_dim
            assert len(result.vector) == expected_dim