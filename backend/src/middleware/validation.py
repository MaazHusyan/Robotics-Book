"""
Input validation middleware for RAG chatbot security.
Provides comprehensive input sanitization and validation for all API endpoints.
"""

import re
import html
import logging
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass
from datetime import datetime
from fastapi import Request, HTTPException, WebSocket
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
import json

from ..utils.errors import ValidationError as CustomValidationError


def sanitize_text(text: str) -> str:
    """Simple text sanitization function."""
    if not text:
        return ""

    # HTML decode
    import html

    text = html.unescape(text)

    # Remove control characters
    import re

    text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


logger = logging.getLogger(__name__)


@dataclass
class ValidationConfig:
    """Configuration for input validation."""

    # Text validation
    max_question_length: int = 1000
    min_question_length: int = 1
    max_context_length: int = 5000
    max_context_chunks: int = 5

    # Content validation
    allowed_tags: Optional[List[str]] = None
    forbidden_patterns: Optional[List[str]] = None
    forbidden_words: Optional[List[str]] = None

    # Rate limiting for validation
    max_validation_attempts: int = 100
    validation_window_seconds: int = 60

    # Security settings
    check_sql_injection: bool = True
    check_xss: bool = True
    check_path_traversal: bool = True
    check_command_injection: bool = True

    def __post_init__(self):
        """Initialize default values."""
        self.forbidden_patterns = self.forbidden_patterns or [
            r"<script[^>]*>.*?</script>",  # Script tags
            r"javascript:",  # JavaScript URLs
            r"on\w+\s*=",  # Event handlers
            r"expression\s*\(",  # CSS expressions
            r"@import",  # CSS imports
            r"union\s+select",  # SQL injection
            r"drop\s+table",  # SQL injection
            r"insert\s+into",  # SQL injection
            r"update\s+.*set",  # SQL injection
            r"delete\s+from",  # SQL injection
            r"\.\./",  # Path traversal
            r"cmd\.exe",  # Command injection
            r"/bin/",  # Command injection
            r"powershell",  # Command injection
        ]

        self.forbidden_words = self.forbidden_words or [
            "password",
            "secret",
            "token",
            "key",
            "auth",
            "admin",
            "root",
            "sudo",
            "privilege",
        ]

        if self.forbidden_words is None:
            self.forbidden_words = [
                "password",
                "secret",
                "token",
                "key",
                "auth",
                "admin",
                "root",
                "sudo",
                "privilege",
            ]


class QuestionValidator(BaseModel):
    """Pydantic model for question validation."""

    question: str
    context_chunks: Optional[List[str]] = None
    session_id: Optional[str] = None

    class Config:
        str_strip_whitespace = True
        str_min_length = 1
        str_max_length = 1000


class ValidationResult:
    """Result of input validation."""

    def __init__(
        self,
        is_valid: bool = True,
        errors: Optional[List[str]] = None,
        sanitized_data: Optional[Dict[str, Any]] = None,
    ):
        self.is_valid = is_valid
        self.errors = errors or []
        self.sanitized_data = sanitized_data or {}

    def add_error(self, error: str):
        """Add validation error."""
        self.errors.append(error)
        self.is_valid = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "sanitized_data": self.sanitized_data,
        }


class InputValidator:
    """Main input validation implementation."""

    def __init__(self, config: Optional[ValidationConfig] = None):
        self.config = config or ValidationConfig()
        self.validation_attempts = {}

    def validate_question(self, question: str) -> ValidationResult:
        """Validate a question string."""
        result = ValidationResult()

        # Length validation
        if not question or len(question.strip()) < self.config.min_question_length:
            result.add_error("Question cannot be empty")

        if len(question) > self.config.max_question_length:
            result.add_error(
                f"Question too long (max {self.config.max_question_length} characters)"
            )

        # Content validation
        if self._contains_forbidden_patterns(question):
            result.add_error("Question contains forbidden content")

        if self._contains_sql_injection(question):
            result.add_error("Question appears to contain SQL injection")

        if self._contains_xss(question):
            result.add_error("Question appears to contain XSS")

        if self._contains_command_injection(question):
            result.add_error("Question appears to contain command injection")

        # Sanitize question
        if result.is_valid:
            sanitized_question = sanitize_text(question)
            result.sanitized_data["question"] = sanitized_question

        return result

    def validate_context_chunks(self, context_chunks: List[str]) -> ValidationResult:
        """Validate context chunks."""
        result = ValidationResult()

        if not context_chunks:
            return result  # Context chunks are optional

        # Count validation
        if len(context_chunks) > self.config.max_context_chunks:
            result.add_error(
                f"Too many context chunks (max {self.config.max_context_chunks})"
            )

        # Validate each chunk
        sanitized_chunks = []
        for i, chunk in enumerate(context_chunks):
            if not chunk or not chunk.strip():
                result.add_error(f"Context chunk {i + 1} is empty")
                continue

            if len(chunk) > self.config.max_context_length:
                result.add_error(
                    f"Context chunk {i + 1} too long (max {self.config.max_context_length} characters)"
                )
                continue

            # Content validation
            if self._contains_forbidden_patterns(chunk):
                result.add_error(f"Context chunk {i + 1} contains forbidden content")
                continue

            # Sanitize chunk
            sanitized_chunk = sanitize_text(chunk)
            sanitized_chunks.append(sanitized_chunk)

        if result.is_valid:
            result.sanitized_data["context_chunks"] = sanitized_chunks

        return result

    def validate_session_id(self, session_id: Optional[str]) -> ValidationResult:
        """Validate session ID."""
        result = ValidationResult()

        if not session_id:
            return result  # Session ID is optional

        # Basic format validation
        if not re.match(r"^[a-zA-Z0-9_-]+$", session_id):
            result.add_error("Invalid session ID format")

        if len(session_id) > 64:
            result.add_error("Session ID too long (max 64 characters)")

        if result.is_valid:
            result.sanitized_data["session_id"] = session_id

        return result

    def validate_websocket_message(
        self, message_data: Dict[str, Any]
    ) -> ValidationResult:
        """Validate WebSocket message data."""
        result = ValidationResult()

        try:
            # Validate message structure
            if "type" not in message_data:
                result.add_error("Message missing 'type' field")

            if "data" not in message_data:
                result.add_error("Message missing 'data' field")

            if not result.is_valid:
                return result

            message_type = message_data["type"]
            data = message_data["data"]

            # Validate based on message type
            if message_type == "question":
                return self._validate_question_message(data)
            elif message_type in ["response_start", "response_chunk", "response_end"]:
                # These are server-to-client messages, no validation needed
                return result
            else:
                result.add_error(f"Unknown message type: {message_type}")

        except Exception as e:
            result.add_error(f"Message validation error: {str(e)}")

        return result

    def _validate_question_message(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate question message data."""
        result = ValidationResult()

        # Validate question
        question = data.get("question", "")
        question_result = self.validate_question(question)
        if not question_result.is_valid:
            result.errors.extend(question_result.errors)
            result.is_valid = False

        # Validate context chunks
        context_chunks = data.get("context_chunks", [])
        context_result = self.validate_context_chunks(context_chunks)
        if not context_result.is_valid:
            result.errors.extend(context_result.errors)
            result.is_valid = False

        # Validate session ID
        session_id = data.get("session_id")
        session_result = self.validate_session_id(session_id)
        if not session_result.is_valid:
            result.errors.extend(session_result.errors)
            result.is_valid = False

        # Combine sanitized data
        if result.is_valid:
            result.sanitized_data.update(question_result.sanitized_data)
            result.sanitized_data.update(context_result.sanitized_data)
            result.sanitized_data.update(session_result.sanitized_data)

        return result

    def _contains_forbidden_patterns(self, text: str) -> bool:
        """Check if text contains forbidden patterns."""
        if not self.config.forbidden_patterns:
            return False

        text_lower = text.lower()

        for pattern in self.config.forbidden_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True

        return False

    def _contains_sql_injection(self, text: str) -> bool:
        """Check for SQL injection patterns."""
        if not self.config.check_sql_injection:
            return False

        sql_patterns = [
            r"union\s+select",
            r"drop\s+table",
            r"insert\s+into",
            r"update\s+.*set",
            r"delete\s+from",
            r"exec\s*\(",
            r"execute\s*\(",
            r"sp_executesql",
            r"xp_cmdshell",
            r"'--",
            r"--",
            r"/\*.*\*/",
            r";\s*drop",
            r";\s*delete",
            r";\s*insert",
        ]

        text_lower = text.lower()
        for pattern in sql_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True

        return False

    def _contains_xss(self, text: str) -> bool:
        """Check for XSS patterns."""
        if not self.config.check_xss:
            return False

        xss_patterns = [
            r"<script[^>]*>",
            r"</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"expression\s*\(",
            r"@import",
            r"<iframe",
            r"<object",
            r"<embed",
            r"<link",
            r"<meta",
            r"<form",
            r"<input",
            r"vbscript:",
            r"data:text/html",
        ]

        text_lower = text.lower()
        for pattern in xss_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True

        return False

    def _contains_command_injection(self, text: str) -> bool:
        """Check for command injection patterns."""
        if not self.config.check_command_injection:
            return False

        cmd_patterns = [
            r"cmd\.exe",
            r"/bin/",
            r"/etc/",
            r"powershell",
            r"bash\s+-",
            r"sh\s+-",
            r"eval\s*\(",
            r"exec\s*\(",
            r"system\s*\(",
            r"passthru\s*\(",
            r"shell_exec\s*\(",
            r"`[^`]*`",  # Backticks
            r"\$\([^)]*\)",  # Command substitution
            r">\s*/dev/",
            r"|\s*nc\s+",
            r"&&\s*",
            r";\s*rm\s",
            r";\s*cat\s",
        ]

        text_lower = text.lower()
        for pattern in cmd_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True

        return False


class ValidationMiddleware:
    """FastAPI middleware for input validation."""

    def __init__(self, config: Optional[ValidationConfig] = None):
        self.validator = InputValidator(config)

    async def __call__(self, request: Request, call_next: Callable):
        """Middleware call handler."""
        # Only validate POST/PUT/PATCH requests
        if request.method not in ["POST", "PUT", "PATCH"]:
            return await call_next(request)

        try:
            # Get request body
            body = await request.body()

            if not body:
                return await call_next(request)

            # Parse JSON
            try:
                data = json.loads(body.decode())
            except json.JSONDecodeError:
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": "invalid_json",
                        "message": "Invalid JSON in request body",
                    },
                )

            # Validate based on path
            path = request.url.path

            if path == "/api/chat":
                # Validate chat message
                validation_result = self.validator.validate_websocket_message(data)
            else:
                # Generic validation for other endpoints
                validation_result = ValidationResult()

            if not validation_result.is_valid:
                logger.warning(
                    f"Validation failed for {path}: {validation_result.errors}"
                )

                return JSONResponse(
                    status_code=400,
                    content={
                        "error": "validation_failed",
                        "message": "Input validation failed",
                        "errors": validation_result.errors,
                    },
                )

            # Replace request body with sanitized data
            if validation_result.sanitized_data:
                sanitized_body = json.dumps(validation_result.sanitized_data).encode()

                # Create a new request with sanitized body
                async def receive():
                    return {"type": "http.request", "body": sanitized_body}

                request = Request(request.scope, receive)

            return await call_next(request)

        except Exception as e:
            logger.error(f"Validation middleware error: {e}")

            return JSONResponse(
                status_code=500,
                content={
                    "error": "validation_error",
                    "message": "Internal validation error",
                },
            )


# WebSocket validator
async def validate_websocket_message(
    message_data: Dict[str, Any], validator: Optional[InputValidator] = None
) -> ValidationResult:
    """Validate WebSocket message."""
    if validator is None:
        validator = InputValidator()

    return validator.validate_websocket_message(message_data)


# Decorator for validation
def validate_input(
    max_length: int = 1000,
    check_injection: bool = True,
    check_xss: bool = True,
):
    """Decorator to add input validation to endpoints."""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract request from args
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if request is None:
                # Try to get from kwargs
                request = kwargs.get("request")

            if request is None:
                # No request found, skip validation
                return await func(*args, **kwargs)

            # Create validator
            config = ValidationConfig(
                max_question_length=max_length,
                check_sql_injection=check_injection,
                check_xss=check_xss,
            )

            validator = InputValidator(config)

            # Get request body
            body = await request.body()
            if body:
                try:
                    data = json.loads(body.decode())
                    validation_result = validator.validate_websocket_message(data)

                    if not validation_result.is_valid:
                        raise HTTPException(
                            status_code=400,
                            detail={
                                "error": "validation_failed",
                                "errors": validation_result.errors,
                            },
                        )

                    # Update request with sanitized data
                    if validation_result.sanitized_data:

                        async def receive():
                            return {
                                "type": "http.request",
                                "body": json.dumps(
                                    validation_result.sanitized_data
                                ).encode(),
                            }

                        request = Request(request.scope, receive)
                        # Update args/kwargs with new request
                        new_args = list(args)
                        for i, arg in enumerate(new_args):
                            if isinstance(arg, Request):
                                new_args[i] = request
                                break
                        else:
                            kwargs["request"] = request

                        args = tuple(new_args)

                except json.JSONDecodeError:
                    raise HTTPException(
                        status_code=400,
                        detail={"error": "invalid_json", "message": "Invalid JSON"},
                    )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


# Health check for validation
async def validation_health_check() -> Dict[str, Any]:
    """Perform health check on validation system."""
    try:
        config = ValidationConfig()
        validator = InputValidator(config)

        # Test validation
        test_cases = [
            ("What is robotics?", True),
            ("<script>alert('xss')</script>", False),
            ("'; DROP TABLE users; --", False),
            ("", False),
        ]

        passed = 0
        total = len(test_cases)

        for test_input, expected_valid in test_cases:
            result = validator.validate_question(test_input)
            if result.is_valid == expected_valid:
                passed += 1

        health_status = {
            "status": "healthy" if passed == total else "degraded",
            "test_results": f"{passed}/{total} tests passed",
            "timestamp": datetime.now().isoformat(),
        }

        return health_status

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }
