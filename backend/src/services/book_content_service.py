from typing import List, Optional
from src.models.api_models import BookContent
from src.exceptions import BookContentNotFoundError, InvalidChapterError, InvalidSectionError


class BookContentService:
    """Service class for handling book content operations."""

    def __init__(self):
        # In a real implementation, this would connect to a database or file system
        # For now, we'll use a simple in-memory store for demonstration
        self._book_contents: List[BookContent] = []
        self._initialize_sample_content()

    def _initialize_sample_content(self):
        """Initialize with sample book content for testing."""
        sample_content = BookContent(
            title="Introduction to Robotics",
            content="Robotics is an interdisciplinary branch of engineering and science that includes mechanical engineering, electrical engineering, computer science, and others.",
            chapter="1",
            section="1.1",
            metadata={"author": "Robotics Expert", "tags": ["introduction", "overview"]}
        )
        self._book_contents.append(sample_content)

    def get_content_by_chapter_and_section(self, chapter: str, section: str) -> BookContent:
        """Get book content by chapter and section."""
        for content in self._book_contents:
            if content.chapter == chapter and content.section == section:
                return content
        raise BookContentNotFoundError(f"Content not found for chapter {chapter}, section {section}")

    def get_content_by_chapter(self, chapter: str) -> List[BookContent]:
        """Get all content for a specific chapter."""
        if not chapter:
            raise InvalidChapterError("Chapter cannot be empty")

        chapter_contents = [content for content in self._book_contents if content.chapter == chapter]
        if not chapter_contents:
            raise BookContentNotFoundError(f"No content found for chapter {chapter}")

        return chapter_contents

    def get_all_content(self) -> List[BookContent]:
        """Get all book content."""
        return self._book_contents

    def search_content(self, query: str) -> List[BookContent]:
        """Search for content containing the query string."""
        if not query:
            return []

        query_lower = query.lower()
        matching_contents = []

        for content in self._book_contents:
            if (query_lower in content.title.lower() or
                query_lower in content.content.lower() or
                query_lower in ' '.join(content.metadata.get('tags', [])).lower()):
                matching_contents.append(content)

        return matching_contents