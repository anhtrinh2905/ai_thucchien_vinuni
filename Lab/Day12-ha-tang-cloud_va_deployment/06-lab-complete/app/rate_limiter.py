"""Sliding window rate limiter — Redis-backed with in-memory fallback."""
import time
from collections import defaultdict, deque

from fastapi import HTTPException

from app.config import settings
from app.redis_client import get_redis

_memory_windows: dict[str, deque] = defaultdict(deque)


def check_rate_limit(user_id: str) -> None:
    """
    Sliding window rate limiter.
    Raises HTTPException(429) when limit exceeded.
    """
    limit = settings.rate_limit_per_minute
    window = 60
    now = time.time()
    key = f"ratelimit:{user_id}"

    r = get_redis()
    if r:
        try:
            pipe = r.pipeline()
            pipe.zremrangebyscore(key, 0, now - window)
            pipe.zcard(key)
            count = pipe.execute()[1]
            if count >= limit:
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded: {limit} req/min",
                    headers={"Retry-After": "60"},
                )
            r.zadd(key, {str(now): now})
            r.expire(key, window + 1)
            return
        except HTTPException:
            raise
        except Exception:
            pass

    bucket = _memory_windows[user_id]
    while bucket and bucket[0] < now - window:
        bucket.popleft()
    if len(bucket) >= limit:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: {limit} req/min",
            headers={"Retry-After": "60"},
        )
    bucket.append(now)
