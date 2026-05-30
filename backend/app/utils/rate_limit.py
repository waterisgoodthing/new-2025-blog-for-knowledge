import time
from collections import defaultdict

from fastapi import HTTPException


class RateLimiter:
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._store: dict[str, list[float]] = defaultdict(list)

    def check(self, key: str) -> None:
        now = time.time()
        timestamps = self._store[key]
        self._store[key] = [t for t in timestamps if now - t < self.window_seconds]
        if len(self._store[key]) >= self.max_requests:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Max {self.max_requests} requests per {self.window_seconds}s.",
            )
        self._store[key].append(now)
