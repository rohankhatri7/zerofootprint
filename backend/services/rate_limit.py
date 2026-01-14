import time
from redis import Redis


class RateLimitError(Exception):
    pass


def enforce_rate_limit(redis: Redis, key: str, window_seconds: int = 60) -> None:
    now = int(time.time())
    bucket = now // window_seconds
    redis_key = f"rate:{key}:{bucket}"
    count = redis.incr(redis_key)
    if count == 1:
        redis.expire(redis_key, window_seconds)
    if count > 5:
        raise RateLimitError("Too many requests, slow down")
