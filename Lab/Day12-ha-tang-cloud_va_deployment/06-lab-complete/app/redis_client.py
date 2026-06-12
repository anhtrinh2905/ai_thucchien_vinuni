"""Shared Redis client with fast timeout — tránh hang khi Redis unreachable."""
import redis

from app.config import settings

_client: redis.Redis | None = None

REDIS_TIMEOUT_SEC = 2


def get_redis() -> redis.Redis | None:
    global _client
    if not settings.redis_url:
        return None
    if _client is None:
        _client = redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=REDIS_TIMEOUT_SEC,
            socket_timeout=REDIS_TIMEOUT_SEC,
        )
    return _client


def ping_redis() -> bool:
    try:
        get_redis().ping()
        return True
    except Exception:
        return False
