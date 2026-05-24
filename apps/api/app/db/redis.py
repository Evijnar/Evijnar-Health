"""Redis client helper (async) for the API.

Provides a shared aioredis client instance with lazy initialization so code
can call `await get_redis()` from FastAPI lifespans or route handlers.
"""

from typing import Optional
import aioredis
from app.config import settings

_redis: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    """Get a shared aioredis Redis instance. Lazy-initializes on first call."""
    global _redis
    if _redis is None:
        if not settings.redis_url:
            raise RuntimeError("Redis URL not configured in settings.redis_url")
        _redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    return _redis


async def close_redis() -> None:
    """Close the shared Redis connection pool."""
    global _redis
    if _redis is not None:
        try:
            await _redis.close()
        finally:
            _redis = None
