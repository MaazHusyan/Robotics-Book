from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
import logging
from src.utils.logging import get_logger

logger = get_logger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Log the incoming request
        logger.info(f"Request: {request.method} {request.url.path}")

        response = await call_next(request)

        # Calculate request processing time
        process_time = time.time() - start_time

        # Log the response
        logger.info(f"Response: {response.status_code} in {process_time:.2f}s")

        return response