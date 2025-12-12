import re
from typing import Dict, Any, List, Optional
from ..utils.errors import ValidationError


class ContentValidator:
    """Service for validating content and inputs."""

    def __init__(self):
        # Define validation rules
        self.max_question_length = 1000
        self.max_context_chunks = 5
        self.max_chunk_length = 1000
        self.min_chunk_length = 100

        # Dangerous patterns to block
        self.dangerous_patterns = [
            r"<script[^>]*>.*?</script>",  # Script tags
            r"javascript:",  # JavaScript URLs
            r"data:",  # Data URLs
            r"vbscript:",  # VBScript URLs
            r"onload\s*=",  # Event handlers
            r"onerror\s*=",  # Event handlers
            r"onclick\s*=",  # Event handlers
            r"onmouseover\s*=",  # Event handlers
            r"<iframe[^>]*>",  # Iframes
            r"<object[^>]*>",  # Objects
            r"<embed[^>]*>",  # Embeds
        ]

        # Allowed HTML tags (for content sanitization)
        self.allowed_tags = [
            "p",
            "br",
            "strong",
            "em",
            "u",
            "i",
            "b",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "ul",
            "ol",
            "li",
            "blockquote",
            "code",
            "pre",
        ]

    def validate_question(self, question: str) -> Dict[str, Any]:
        """
        Validate a user question.

        Args:
            question: User's question

        Returns:
            Dictionary with validation result

        Raises:
            ValidationError: If question is invalid
        """
        if not question:
            raise ValidationError("Question cannot be empty")

        question = question.strip()

        if len(question) == 0:
            raise ValidationError("Question cannot be empty")

        if len(question) > self.max_question_length:
            raise ValidationError(
                f"Question exceeds {self.max_question_length} characters"
            )

        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            if re.search(pattern, question, re.IGNORECASE):
                raise ValidationError("Question contains potentially unsafe content")

        # Check for spam patterns
        if self._is_spam(question):
            raise ValidationError("Question appears to be spam")

        return {
            "is_valid": True,
            "question": question,
            "length": len(question),
            "word_count": len(question.split()),
            "language": self._detect_language(question),
        }

    def validate_context_chunks(self, context_chunks: List[str]) -> Dict[str, Any]:
        """
        Validate highlighted context chunks.

        Args:
            context_chunks: List of highlighted text chunks

        Returns:
            Dictionary with validation result

        Raises:
            ValidationError: If context chunks are invalid
        """
        if not context_chunks:
            return {"is_valid": True, "chunks": [], "total_length": 0, "chunk_count": 0}

        if len(context_chunks) > self.max_context_chunks:
            raise ValidationError(
                f"Too many context chunks (max {self.max_context_chunks})"
            )

        validated_chunks = []
        total_length = 0

        for i, chunk in enumerate(context_chunks):
            if not chunk or not chunk.strip():
                continue  # Skip empty chunks

            chunk = chunk.strip()

            if len(chunk) > self.max_chunk_length:
                raise ValidationError(f"Context chunk {i + 1} exceeds maximum length")

            # Check for dangerous patterns
            for pattern in self.dangerous_patterns:
                if re.search(pattern, chunk, re.IGNORECASE):
                    raise ValidationError(
                        f"Context chunk {i + 1} contains unsafe content"
                    )

            validated_chunks.append(chunk)
            total_length += len(chunk)

        return {
            "is_valid": True,
            "chunks": validated_chunks,
            "total_length": total_length,
            "chunk_count": len(validated_chunks),
        }

    def validate_content_chunk(
        self, content: str, source_file: str = None
    ) -> Dict[str, Any]:
        """
        Validate a content chunk for storage.

        Args:
            content: Content chunk text
            source_file: Optional source file path

        Returns:
            Dictionary with validation result

        Raises:
            ValidationError: If content chunk is invalid
        """
        if not content:
            raise ValidationError("Content chunk cannot be empty")

        content = content.strip()

        if len(content) < self.min_chunk_length:
            raise ValidationError(
                f"Content chunk too short (min {self.min_chunk_length} characters)"
            )

        if len(content) > self.max_chunk_length:
            raise ValidationError(
                f"Content chunk too long (max {self.max_chunk_length} characters)"
            )

        # Check for meaningful content
        if not self._has_meaningful_content(content):
            raise ValidationError("Content chunk lacks meaningful content")

        return {
            "is_valid": True,
            "content": content,
            "length": len(content),
            "word_count": len(content.split()),
            "sentence_count": len(re.split(r"[.!?]+", content)),
            "language": self._detect_language(content),
            "source_file": source_file,
        }

    def sanitize_html(self, content: str) -> str:
        """
        Sanitize HTML content by removing dangerous tags.

        Args:
            content: Content with potential HTML

        Returns:
            Sanitized content
        """
        # Remove dangerous tags
        for pattern in self.dangerous_patterns:
            content = re.sub(pattern, "", content, flags=re.IGNORECASE)

        # Allow only safe tags
        # This is a simple implementation - in production, use a proper HTML sanitizer
        tag_pattern = r"<(/?)(\w+)([^>]*)>"

        def replace_tag(match):
            closing, tag_name, attributes = match.groups()
            if tag_name.lower() in self.allowed_tags:
                return match.group(0)
            return ""  # Remove disallowed tags

        content = re.sub(tag_pattern, replace_tag, content, flags=re.IGNORECASE)

        return content

    def _is_spam(self, text: str) -> bool:
        """Check if text appears to be spam."""
        spam_indicators = [
            r"(click\s+here)",  # Click bait
            r"(buy\s+now)",  # Commercial content
            r"(free\s+money)",  # Scam patterns
            r"(urgent\s+action)",  # Fake urgency
            r"(\w{3,})\1{2,}",  # Repeated characters
            r"(https?://\S+)",  # Multiple URLs
        ]

        spam_score = 0
        text_lower = text.lower()

        for pattern in spam_indicators:
            if re.search(pattern, text_lower):
                spam_score += 1

        # Check for excessive capitalization
        caps_ratio = sum(1 for c in text if c.isupper()) / max(1, len(text))
        if caps_ratio > 0.5:
            spam_score += 1

        # Check for excessive punctuation
        punct_ratio = sum(1 for c in text if not c.isalnum()) / max(1, len(text))
        if punct_ratio > 0.3:
            spam_score += 1

        return spam_score >= 2  # Threshold for spam detection

    def _has_meaningful_content(self, content: str) -> bool:
        """Check if content has meaningful text."""
        # Remove whitespace and punctuation
        clean_content = re.sub(r"[^\w\s]", "", content)

        # Check minimum word count
        words = clean_content.split()
        if len(words) < 10:
            return False

        # Check for repetitive content
        unique_words = set(word.lower() for word in words)
        if len(unique_words) < len(words) * 0.3:  # Less than 30% unique words
            return False

        return True

    def _detect_language(self, text: str) -> str:
        """Simple language detection based on character patterns."""
        # This is a very basic implementation
        # In production, use a proper language detection library

        # Check for common English words
        english_words = [
            "the",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
        ]
        words = text.lower().split()
        english_word_count = sum(1 for word in words if word in english_words)

        if english_word_count > len(words) * 0.1:  # 10% common English words
            return "en"

        return "unknown"

    def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation service statistics."""
        return {
            "max_question_length": self.max_question_length,
            "max_context_chunks": self.max_context_chunks,
            "max_chunk_length": self.max_chunk_length,
            "min_chunk_length": self.min_chunk_length,
            "allowed_tags": self.allowed_tags,
            "dangerous_patterns_count": len(self.dangerous_patterns),
        }

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on validation service."""
        try:
            # Test question validation
            test_question = self.validate_question("What is robotics?")

            # Test context validation
            test_context = self.validate_context_chunks(["This is a test context"])

            # Test content validation
            test_content = self.validate_content_chunk(
                "This is a test content chunk with meaningful text."
            )

            return {
                "status": "healthy",
                "question_validation": {
                    "test_passed": test_question["is_valid"],
                    "test_length": test_question["length"],
                },
                "context_validation": {
                    "test_passed": test_context["is_valid"],
                    "test_chunk_count": test_context["chunk_count"],
                },
                "content_validation": {
                    "test_passed": test_content["is_valid"],
                    "test_length": test_content["length"],
                },
                "validation_stats": self.get_validation_stats(),
            }

        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


# Singleton instance
content_validator = ContentValidator()
