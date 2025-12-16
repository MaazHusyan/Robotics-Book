from fastapi import APIRouter, Query
from typing import List, Optional
from src.models.api_models import BookContent
from src.services.book_content_service import BookContentService
from src.exceptions import BookContentNotFoundError

router = APIRouter()
service = BookContentService()

@router.get("/book/content", response_model=BookContent)
def get_book_content(
    chapter: str = Query(..., description="Chapter identifier"),
    section: str = Query(None, description="Section identifier")
):
    """Get book content by chapter and optional section."""
    try:
        if section:
            return service.get_content_by_chapter_and_section(chapter, section)
        else:
            # If no section is specified, return the first content for the chapter
            contents = service.get_content_by_chapter(chapter)
            if contents:
                return contents[0]
            else:
                raise BookContentNotFoundError(f"No content found for chapter {chapter}")
    except BookContentNotFoundError as e:
        raise e
    except Exception as e:
        raise BookContentNotFoundError(f"Error retrieving content: {str(e)}")

@router.get("/book/chapter/{chapter}", response_model=List[BookContent])
def get_chapter_content(chapter: str):
    """Get all content for a specific chapter."""
    try:
        return service.get_content_by_chapter(chapter)
    except BookContentNotFoundError as e:
        raise e
    except Exception as e:
        raise BookContentNotFoundError(f"Error retrieving chapter content: {str(e)}")

@router.get("/book/search", response_model=List[BookContent])
def search_book_content(query: str = Query(..., description="Search query")):
    """Search for content containing the query string."""
    try:
        if not query.strip():
            return []
        return service.search_content(query)
    except Exception as e:
        raise BookContentNotFoundError(f"Error searching content: {str(e)}")

@router.get("/book/all", response_model=List[BookContent])
def get_all_book_content():
    """Get all book content."""
    try:
        return service.get_all_content()
    except Exception as e:
        raise BookContentNotFoundError(f"Error retrieving all content: {str(e)}")