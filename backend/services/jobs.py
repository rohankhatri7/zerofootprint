from rq import Queue
from redis import Redis
from settings import settings


def get_queue() -> Queue:
    redis = Redis.from_url(settings.redis_url)
    return Queue("default", connection=redis)
