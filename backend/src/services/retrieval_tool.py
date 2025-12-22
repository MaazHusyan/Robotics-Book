"""
Retrieval tool function adapted from rag_agent.py reference file.

This module provides the retrieve_book_data function as a tool for the agent.
"""
from typing import List, Dict, Optional
from agents import function_tool
from src.utils.embedding_utils import get_embedding
from src.utils.qdrant_retriever import retrieve_data_from_qdrant_collection


@function_tool(is_enabled=True)
def retrieve_book_data(query: str = None, limit: int = 5) -> List[Dict]:
    """
    Retrieve book data from Qdrant collection based on a query.
    This tool searches the book content for relevant information to answer user questions.
    This function adapts the implementation from rag_agent.py reference file.

    Args:
        query: Search query for similarity search (optional)
        limit: Number of records to retrieve (default 5)

    Returns:
        List of retrieved records with id, score, and payload containing book content
    """
    Collection_name = "My_Book_Embadding"

    if query is None:
        # Retrieve records without similarity search
        records = retrieve_data_from_qdrant_collection(
            collection_name=Collection_name,
            limit=limit
        )
    else:
        # Convert text query to embedding
        query_vector = get_embedding(query)

        # Perform similarity search with query vector
        records = retrieve_data_from_qdrant_collection(
            collection_name=Collection_name,
            query_vector=query_vector,
            limit=limit
        )

    # Return records with better structure for the agent
    if records:
        # Process records to make content more accessible to the agent
        processed_records = []
        for record in records:
            processed_record = {
                "id": record.get("id"),
                "score": record.get("score"),
                "metadata": record.get("payload", {}),
                "summary": f"Found relevant book section with metadata: {dict(list(record.get('payload', {}).items())[:5])}"  # Show first 5 metadata items
            }
            processed_records.append(processed_record)

        # Only return records that have some form of content or useful metadata
        return processed_records
    else:
        # Return an indication that no relevant content was found
        return [{"id": "no_content", "score": 0, "metadata": {}, "summary": "No relevant content found in the book for this query"}]