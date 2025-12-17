import time
import threading
from typing import Optional
from collections import deque


class RateLimiter:
    """
    A rate limiter to control API calls based on requests per time window.
    """
    def __init__(self, max_requests: int, time_window_seconds: int):
        self.max_requests = max_requests
        self.time_window_seconds = time_window_seconds
        self.requests = deque()
        self.lock = threading.Lock()

    def acquire(self) -> bool:
        """
        Acquire a request slot, blocking if necessary.
        Returns True if the request can proceed, False otherwise.
        """
        with self.lock:
            now = time.time()

            # Remove requests that are outside the time window
            while self.requests and self.requests[0] <= now - self.time_window_seconds:
                self.requests.popleft()

            # Check if we're under the limit
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True
            else:
                # Calculate how long to wait until the next slot is available
                wait_time = self.requests[0] + self.time_window_seconds - now
                if wait_time > 0:
                    time.sleep(wait_time)
                    # After waiting, add the new request
                    self.requests.append(time.time())
                    return True
                return False

    def can_acquire(self) -> bool:
        """
        Check if a request can be made without blocking.
        """
        with self.lock:
            now = time.time()

            # Remove requests that are outside the time window
            while self.requests and self.requests[0] <= now - self.time_window_seconds:
                self.requests.popleft()

            return len(self.requests) < self.max_requests


class CohereRateLimiter:
    """
    Specialized rate limiter for Cohere API calls.
    """
    def __init__(self, max_requests: int = 100, time_window_seconds: int = 60):
        self.rate_limiter = RateLimiter(max_requests, time_window_seconds)

    def wait_if_needed(self):
        """
        Wait if needed to respect rate limits before making an API call.
        """
        while not self.rate_limiter.can_acquire():
            time.sleep(0.1)  # Small sleep to avoid busy waiting
        self.rate_limiter.acquire()  # Acquire the slot