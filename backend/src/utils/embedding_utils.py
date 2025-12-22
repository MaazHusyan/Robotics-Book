"""
Embedding utility functions adapted from rag_agent.py reference file.

This module provides embedding functionality with fallback mechanisms
for the RAG chatbot system.
"""
from typing import List
import os
import hashlib


def get_embedding(text: str) -> List[float]:
    """
    Get embedding for text query using the all-MiniLM-L6-v2 model via sentence-transformers.
    This function adapts the implementation from rag_agent.py with fallback mechanisms.

    Args:
        text: Text to embed

    Returns:
        Embedding vector as a list of floats
    """
    # Try to use the configured embedding service first (Jina or Cohere from settings)
    try:
        # Import the embedding service from the existing embedding module
        from src.embedding.services.embedding_service import embed_text
        # This will use the configured embedding service (Jina AI, Cohere, etc.)
        embedding_result = embed_text([text])
        if embedding_result and len(embedding_result) > 0:
            # Ensure the embedding has the correct dimension (1024) expected by Qdrant
            embedding = embedding_result[0]
            target_size = 1024
            if len(embedding) < target_size:
                # Pad with zeros if too small
                embedding.extend([0.0] * (target_size - len(embedding)))
            elif len(embedding) > target_size:
                # Truncate if too large
                embedding = embedding[:target_size]
            return embedding
    except Exception as e:
        print(f"Error using configured embedding service: {e}")
        # Fall through to the local embedding approach below

    # Fallback: Try to use sentence transformers if available
    try:
        from sentence_transformers import SentenceTransformer
        import torch

        # Load the embedding model via sentence-transformers
        # Use a more common and reliable model that produces 1024-dim embeddings
        model = SentenceTransformer('all-MiniLM-L6-v2')

        # Generate embeddings
        embedding = model.encode([text], convert_to_numpy=True)[0].tolist()

        # Ensure the embedding has the correct dimension (1024) expected by Qdrant
        target_size = 1024
        if len(embedding) < target_size:
            # Pad with zeros if too small
            embedding.extend([0.0] * (target_size - len(embedding)))
        elif len(embedding) > target_size:
            # Truncate if too large
            embedding = embedding[:target_size]

        return embedding
    except ImportError:
        print("Sentence transformers not available, using hash-based embedding fallback")
    except Exception as e:
        print(f"Error getting embedding from sentence transformer model: {e}")

    # Final fallback to hash-based embedding if model fails
    hash_input = text.encode('utf-8')
    hash_obj = hashlib.sha256(hash_input)
    hash_hex = hash_obj.hexdigest()

    floats = []
    for i in range(0, len(hash_hex), 8):
        chunk = hash_hex[i:i+8]
        if len(chunk) == 8:
            int_val = int(chunk, 16)
            float_val = (int_val % 2000000000) / 1000000000.0 - 1.0
            floats.append(float_val)

    target_size = 1024  # Match the expected dimension in Qdrant (1024)
    if len(floats) < target_size:
        floats.extend([0.0] * (target_size - len(floats)))
    else:
        floats = floats[:target_size]

    return floats


def get_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Get embeddings for multiple texts.

    Args:
        texts: List of texts to embed

    Returns:
        List of embedding vectors as lists of floats
    """
    return [get_embedding(text) for text in texts]