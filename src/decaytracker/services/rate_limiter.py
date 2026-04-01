"""IP-based rate limiter — in-memory, async-safe with asyncio.Lock."""
import asyncio
import time
from collections import defaultdict

from loguru import logger


class RateLimiter:
    """Sliding window rate limiter: max N requests per window (seconds) per key."""

    def __init__(self, max_requests: int = 5, window_seconds: int = 3600):
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._requests: dict[str, list[float]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def check(self, key: str) -> bool:
        """Return True if request is allowed, False if rate-limited."""
        now = time.monotonic()
        cutoff = now - self._window_seconds

        async with self._lock:
            # Prune expired timestamps
            timestamps = self._requests[key]
            self._requests[key] = [t for t in timestamps if t > cutoff]

            if len(self._requests[key]) >= self._max_requests:
                logger.warning("Rate limit exceeded for key={}", key)
                return False

            self._requests[key].append(now)
            return True

    async def cleanup(self) -> int:
        """Remove stale entries. Returns number of keys cleaned."""
        now = time.monotonic()
        cutoff = now - self._window_seconds
        removed = 0

        async with self._lock:
            stale_keys = [
                k for k, timestamps in self._requests.items()
                if not any(t > cutoff for t in timestamps)
            ]
            for k in stale_keys:
                del self._requests[k]
                removed += 1

        return removed


# Global singleton — max 30 audits per hour per IP
audit_rate_limiter = RateLimiter(max_requests=30, window_seconds=3600)
