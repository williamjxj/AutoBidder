"""
Caching Utilities

Provides caching functionality for embeddings and rate limiting.
"""

import hashlib
import time
from typing import Any, Dict, Optional
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class EmbeddingCache:
    """In-memory cache for embeddings to reduce OpenAI API calls."""

    def __init__(self) -> None:
        """Initialize the embedding cache."""
        self._cache: Dict[str, Any] = {}
        self._hits = 0
        self._misses = 0

    def _generate_key(self, text: str, model: str) -> str:
        """Generate cache key from text and model."""
        content = f"{text}:{model}"
        return hashlib.sha256(content.encode()).hexdigest()

    def get(self, text: str, model: str) -> Optional[Any]:
        """Get embedding from cache."""
        key = self._generate_key(text, model)
        if key in self._cache:
            self._hits += 1
            logger.debug(f"Embedding cache HIT (hits: {self._hits}, misses: {self._misses})")
            return self._cache[key]
        self._misses += 1
        logger.debug(f"Embedding cache MISS (hits: {self._hits}, misses: {self._misses})")
        return None

    def set(self, text: str, model: str, embedding: Any) -> None:
        """Store embedding in cache."""
        key = self._generate_key(text, model)
        self._cache[key] = embedding
        logger.debug(f"Cached embedding (cache size: {len(self._cache)})")

    def clear(self) -> None:
        """Clear the cache."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0
        logger.info("Embedding cache cleared")

    @property
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0
        return {
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(hit_rate, 2),
            "size": len(self._cache),
        }


class RateLimiter:
    """Simple in-memory rate limiter."""

    def __init__(self, max_requests: int, window_seconds: int = 60) -> None:
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum requests allowed per window
            window_seconds: Time window in seconds (default: 60)
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: Dict[str, list] = defaultdict(list)

    def is_allowed(self, user_id: str) -> bool:
        """
        Check if request is allowed for user.

        Args:
            user_id: User identifier

        Returns:
            True if request is allowed, False otherwise
        """
        now = time.time()
        cutoff = now - self.window_seconds

        # Remove old requests
        self._requests[user_id] = [
            req_time for req_time in self._requests[user_id] if req_time > cutoff
        ]

        # Check if under limit
        if len(self._requests[user_id]) < self.max_requests:
            self._requests[user_id].append(now)
            return True

        return False

    def get_remaining(self, user_id: str) -> int:
        """Get remaining requests for user."""
        now = time.time()
        cutoff = now - self.window_seconds

        # Count recent requests
        recent = sum(1 for req_time in self._requests[user_id] if req_time > cutoff)
        return max(0, self.max_requests - recent)


# Global cache instances
embedding_cache = EmbeddingCache()
rate_limiter = RateLimiter(max_requests=10, window_seconds=60)
