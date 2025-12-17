import math
from typing import List


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate the cosine similarity between two vectors.

    Args:
        vec1: First vector
        vec2: Second vector

    Returns:
        Cosine similarity value between -1 and 1, where 1 means identical direction
    """
    if len(vec1) != len(vec2):
        raise ValueError("Vectors must have the same dimensionality")

    if len(vec1) == 0:
        return 0.0

    # Calculate dot product
    dot_product = sum(a * b for a, b in zip(vec1, vec2))

    # Calculate magnitudes
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))

    # Handle zero magnitude cases
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0

    # Calculate cosine similarity
    similarity = dot_product / (magnitude1 * magnitude2)

    # Clamp to [-1, 1] range to handle floating point errors
    return max(-1.0, min(1.0, similarity))


def euclidean_distance(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate the Euclidean distance between two vectors.

    Args:
        vec1: First vector
        vec2: Second vector

    Returns:
        Euclidean distance value (0 means identical)
    """
    if len(vec1) != len(vec2):
        raise ValueError("Vectors must have the same dimensionality")

    squared_diffs = [(a - b) ** 2 for a, b in zip(vec1, vec2)]
    return math.sqrt(sum(squared_diffs))


def dot_product_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate the dot product similarity between two vectors.
    This is the raw dot product without normalization.

    Args:
        vec1: First vector
        vec2: Second vector

    Returns:
        Dot product value
    """
    if len(vec1) != len(vec2):
        raise ValueError("Vectors must have the same dimensionality")

    return sum(a * b for a, b in zip(vec1, vec2))