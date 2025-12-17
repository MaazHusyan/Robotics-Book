from typing import Optional
from src.config import settings
from src.embedding.models.embedding_models import EmbeddingConfig
from src.embedding.services.cohere_service import CohereEmbeddingService
from src.embedding.services.jina_service import JinaEmbeddingService
from src.embedding.services.embedding_service_interface import EmbeddingServiceInterface


class EmbeddingServiceFactory:
    """
    Factory for creating embedding services based on configuration.
    """

    @staticmethod
    def create_embedding_service(
        config: Optional[EmbeddingConfig] = None,
        storage_type: str = "qdrant",
        storage_dir: str = "embeddings_storage",
        collection_name: str = "robotics_embeddings"
    ) -> EmbeddingServiceInterface:
        """
        Create an embedding service based on the configured model.

        Args:
            config: Embedding configuration (uses defaults if not provided)
            storage_type: Type of storage to use ("file" or "qdrant") - default is "qdrant"
            storage_dir: Directory to store embeddings (for file-based storage)
            collection_name: Name of the Qdrant collection (for Qdrant storage)

        Returns:
            An instance of an embedding service that implements EmbeddingServiceInterface
        """
        model_name = (config.model if config else settings.EMBEDDING_MODEL).lower()

        # If no config was provided, create one based on settings
        if config is None:
            from src.embedding.models.embedding_models import EmbeddingConfig
            config = EmbeddingConfig()
            config.model = settings.EMBEDDING_MODEL
            config.input_type = settings.EMBEDDING_INPUT_TYPE
            config.truncate = settings.EMBEDDING_TRUNCATE
            config.batch_size = settings.EMBEDDING_BATCH_SIZE
            config.rate_limit_requests = settings.EMBEDDING_RATE_LIMIT_REQUESTS
            config.rate_limit_seconds = settings.EMBEDDING_RATE_LIMIT_SECONDS
            config.retry_attempts = settings.EMBEDDING_RETRY_ATTEMPTS

        if "jina" in model_name:
            # Use Jina service if model name contains "jina"
            return JinaEmbeddingService(
                config=config,
                storage_type=storage_type,
                storage_dir=storage_dir,
                collection_name=collection_name
            )
        else:
            # Default to Cohere service for backward compatibility
            return CohereEmbeddingService(
                config=config,
                storage_type=storage_type,
                storage_dir=storage_dir,
                collection_name=collection_name
            )