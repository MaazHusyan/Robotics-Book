"""
Content sanitization utilities for RAG chatbot security.
Provides text sanitization, HTML cleaning, and content filtering.
"""

import re
import html
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import bleach
import markdown

logger = logging.getLogger(__name__)


@dataclass
class SanitizationConfig:
    """Configuration for content sanitization."""

    # HTML sanitization
    allowed_html_tags: List[str] = None
    allowed_html_attributes: Dict[str, List[str]] = None
    strip_html: bool = True

    # Text cleaning
    normalize_whitespace: bool = True
    remove_control_chars: bool = True
    normalize_unicode: bool = True

    # Content filtering
    remove_urls: bool = False
    remove_emails: bool = True
    remove_phone_numbers: bool = True

    # Markdown processing
    process_markdown: bool = False
    markdown_extensions: List[str] = None

    def __post_init__(self):
        """Initialize default values."""
        if self.allowed_html_tags is None:
            self.allowed_html_tags = [
                "p",
                "br",
                "strong",
                "em",
                "u",
                "i",
                "b",
                "ul",
                "ol",
                "li",
                "blockquote",
                "code",
                "pre",
                "h1",
                "h2",
                "h3",
                "h4",
                "h5",
                "h6",
            ]

        if self.allowed_html_attributes is None:
            self.allowed_html_attributes = {
                "*": ["class"],
                "a": ["href", "title"],
                "img": ["src", "alt", "title", "width", "height"],
            }

        if self.markdown_extensions is None:
            self.markdown_extensions = [
                "fenced_code",
                "codehilite",
                "tables",
                "toc",
                "nl2br",
            ]


class TextSanitizer:
    """Text sanitization and cleaning utilities."""

    def __init__(self, config: Optional[SanitizationConfig] = None):
        self.config = config or SanitizationConfig()

        # Compile regex patterns for performance
        self.url_pattern = re.compile(
            r"https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?",
            re.IGNORECASE,
        )

        self.email_pattern = re.compile(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", re.IGNORECASE
        )

        self.phone_pattern = re.compile(
            r"\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b",
            re.IGNORECASE,
        )

        self.control_char_pattern = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]")

        self.whitespace_pattern = re.compile(r"\s+")

    def sanitize_text(self, text: str) -> str:
        """Sanitize text content."""
        if not text:
            return ""

        # HTML decode
        text = html.unescape(text)

        # Remove control characters
        if self.config.remove_control_chars:
            text = self.control_char_pattern.sub("", text)

        # Remove URLs if configured
        if self.config.remove_urls:
            text = self.url_pattern.sub("[URL_REMOVED]", text)

        # Remove emails if configured
        if self.config.remove_emails:
            text = self.email_pattern.sub("[EMAIL_REMOVED]", text)

        # Remove phone numbers if configured
        if self.config.remove_phone_numbers:
            text = self.phone_pattern.sub("[PHONE_REMOVED]", text)

        # Normalize whitespace
        if self.config.normalize_whitespace:
            text = self.whitespace_pattern.sub(" ", text).strip()

        # Normalize Unicode
        if self.config.normalize_unicode:
            import unicodedata

            text = unicodedata.normalize("NFKC", text)

        return text

    def sanitize_html(self, html_content: str) -> str:
        """Sanitize HTML content."""
        if not html_content:
            return ""

        if self.config.strip_html:
            # Strip all HTML tags
            clean_text = bleach.clean(html_content, tags=[], strip=True)
            return self.sanitize_text(clean_text)
        else:
            # Clean HTML but allow certain tags
            clean_html = bleach.clean(
                html_content,
                tags=self.config.allowed_html_tags,
                attributes=self.config.allowed_html_attributes,
                strip=True,
            )

            # Further sanitize the text content
            return self.sanitize_text(clean_html)

    def process_markdown(self, markdown_text: str) -> str:
        """Process markdown content to safe HTML."""
        if not markdown_text:
            return ""

        # First sanitize the markdown text
        clean_markdown = self.sanitize_text(markdown_text)

        # Convert to HTML
        html_content = markdown.markdown(
            clean_markdown, extensions=self.config.markdown_extensions
        )

        # Sanitize the resulting HTML
        return self.sanitize_html(html_content)

    def extract_text_from_html(self, html_content: str) -> str:
        """Extract plain text from HTML content."""
        if not html_content:
            return ""

        # Use bleach to strip all HTML tags
        plain_text = bleach.clean(html_content, tags=[], strip=True)

        # Further sanitize the extracted text
        return self.sanitize_text(plain_text)

    def validate_content_length(self, text: str, max_length: int = 10000) -> bool:
        """Validate content length."""
        if not text:
            return True

        return len(text) <= max_length

    def truncate_content(
        self, text: str, max_length: int = 10000, suffix: str = "..."
    ) -> str:
        """Truncate content to maximum length."""
        if not text or len(text) <= max_length:
            return text

        return text[: max_length - len(suffix)] + suffix

    def remove_excessive_whitespace(self, text: str) -> str:
        """Remove excessive whitespace from text."""
        if not text:
            return ""

        # Replace multiple newlines with single newline
        text = re.sub(r"\n\s*\n\s*\n", "\n\n", text)

        # Replace multiple spaces with single space
        text = re.sub(r" +", " ", text)

        # Remove leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split("\n")]

        return "\n".join(lines)

    def clean_code_blocks(self, text: str) -> str:
        """Clean and normalize code blocks in text."""
        if not text:
            return ""

        # Normalize code block markers
        text = re.sub(r"```(\w+)?\s*\n", "```\n", text)
        text = re.sub(r"\n\s*```", "\n```", text)

        # Remove excessive empty lines in code blocks
        def clean_code_block(match):
            code_content = match.group(1)
            # Remove excessive empty lines but preserve structure
            code_content = re.sub(r"\n\s*\n\s*\n", "\n\n", code_content)
            return f"```\n{code_content}\n```"

        text = re.sub(r"```(.*?)```", clean_code_block, text, flags=re.DOTALL)

        return text


class ContentFilter:
    """Content filtering and validation utilities."""

    def __init__(self, config: Optional[SanitizationConfig] = None):
        self.config = config or SanitizationConfig()
        self.sanitizer = TextSanitizer(config)

        # Compile content filter patterns
        self.spam_patterns = [
            r"buy\s+now",
            r"click\s+here",
            r"free\s+money",
            r"limited\s+offer",
            r"act\s+now",
            r"call\s+now",
            r"guaranteed",
            r"risk\s+free",
        ]

        self.toxic_patterns = [
            r"\b(hate|kill|die|stupid|idiot|dumb)\b",
            r"\b(curse|swear|damn|hell)\b",
        ]

        self.compiled_spam_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.spam_patterns
        ]
        self.compiled_toxic_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.toxic_patterns
        ]

    def is_spam(self, text: str) -> bool:
        """Check if text appears to be spam."""
        if not text:
            return False

        text_lower = text.lower()

        # Check for spam patterns
        for pattern in self.compiled_spam_patterns:
            if pattern.search(text):
                return True

        # Check for excessive capitalization
        if len(text) > 10:
            uppercase_ratio = sum(1 for c in text if c.isupper()) / len(text)
            if uppercase_ratio > 0.7:  # More than 70% uppercase
                return True

        # Check for excessive punctuation
        punctuation_count = sum(1 for c in text if c in "!?.")
        if punctuation_count > len(text) * 0.2:  # More than 20% punctuation
            return True

        return False

    def is_toxic(self, text: str) -> bool:
        """Check if text contains toxic content."""
        if not text:
            return False

        for pattern in self.compiled_toxic_patterns:
            if pattern.search(text):
                return True

        return False

    def filter_content(self, text: str) -> Dict[str, Any]:
        """Filter and analyze content."""
        if not text:
            return {
                "filtered_content": "",
                "is_spam": False,
                "is_toxic": False,
                "spam_score": 0.0,
                "toxic_score": 0.0,
                "filtered": False,
            }

        # Check for spam and toxicity
        is_spam = self.is_spam(text)
        is_toxic = self.is_toxic(text)

        # Calculate scores (simple heuristic)
        spam_score = 0.0
        toxic_score = 0.0

        if is_spam:
            spam_score = min(
                1.0,
                sum(
                    1 for pattern in self.compiled_spam_patterns if pattern.search(text)
                )
                / len(self.compiled_spam_patterns),
            )

        if is_toxic:
            toxic_score = min(
                1.0,
                sum(
                    1
                    for pattern in self.compiled_toxic_patterns
                    if pattern.search(text)
                )
                / len(self.compiled_toxic_patterns),
            )

        # Filter content if needed
        filtered_content = text
        filtered = False

        if is_spam or is_toxic:
            filtered_content = "[CONTENT_FILTERED]"
            filtered = True
        else:
            # Apply normal sanitization
            filtered_content = self.sanitizer.sanitize_text(text)

        return {
            "filtered_content": filtered_content,
            "is_spam": is_spam,
            "is_toxic": is_toxic,
            "spam_score": spam_score,
            "toxic_score": toxic_score,
            "filtered": filtered,
        }


# Global instances
_text_sanitizer = None
_content_filter = None


def get_text_sanitizer(config: Optional[SanitizationConfig] = None) -> TextSanitizer:
    """Get global text sanitizer instance."""
    global _text_sanitizer
    if _text_sanitizer is None:
        _text_sanitizer = TextSanitizer(config)
    return _text_sanitizer


def get_content_filter(config: Optional[SanitizationConfig] = None) -> ContentFilter:
    """Get global content filter instance."""
    global _content_filter
    if _content_filter is None:
        _content_filter = ContentFilter(config)
    return _content_filter


# Utility functions
def sanitize_text(text: str) -> str:
    """Sanitize text using global sanitizer."""
    sanitizer = get_text_sanitizer()
    return sanitizer.sanitize_text(text)


def sanitize_html(html_content: str) -> str:
    """Sanitize HTML using global sanitizer."""
    sanitizer = get_text_sanitizer()
    return sanitizer.sanitize_html(html_content)


def process_markdown(markdown_text: str) -> str:
    """Process markdown using global sanitizer."""
    sanitizer = get_text_sanitizer()
    return sanitizer.process_markdown(markdown_text)


def filter_content(text: str) -> Dict[str, Any]:
    """Filter content using global filter."""
    filter_instance = get_content_filter()
    return filter_instance.filter_content(text)


# Health check for sanitization
async def sanitization_health_check() -> Dict[str, Any]:
    """Perform health check on sanitization system."""
    try:
        config = SanitizationConfig()
        sanitizer = TextSanitizer(config)
        filter_instance = ContentFilter(config)

        # Test sanitization
        test_cases = [
            ("<script>alert('xss')</script>", "script_removed"),
            ("What is robotics?", "clean_text"),
            ("My email is test@example.com", "email_removed"),
            ("", "empty_text"),
        ]

        passed = 0
        total = len(test_cases)

        for test_input, test_type in test_cases:
            try:
                if test_type == "script_removed":
                    result = sanitizer.sanitize_html(test_input)
                    if "<script>" not in result:
                        passed += 1
                elif test_type == "email_removed":
                    result = sanitizer.sanitize_text(test_input)
                    if "test@example.com" not in result:
                        passed += 1
                else:
                    result = sanitizer.sanitize_text(test_input)
                    if result:
                        passed += 1
            except Exception:
                pass

        # Test content filtering
        spam_test = filter_instance.filter_content("BUY NOW LIMITED OFFER!!!")
        toxic_test = filter_instance.filter_content("This is stupid content")

        health_status = {
            "status": "healthy",
            "sanitization_tests": f"{passed}/{total} passed",
            "spam_filtering": spam_test["is_spam"],
            "toxic_filtering": toxic_test["is_toxic"],
            "timestamp": datetime.now().isoformat(),
        }

        return health_status

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }
