import json
import os
from typing import Any, Optional
import redis
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "300"))

_client = None


def get_redis_client():
    """Return Redis client if available. The API continues working without Redis."""
    global _client
    if not REDIS_URL:
        return None
    if _client is None:
        try:
            _client = redis.from_url(REDIS_URL, decode_responses=True)
            _client.ping()
        except redis.RedisError:
            _client = None
    return _client


def get_cache(key: str) -> Optional[Any]:
    client = get_redis_client()
    if client is None:
        return None
    try:
        value = client.get(key)
        if value is None:
            return None
        return json.loads(value)
    except (redis.RedisError, json.JSONDecodeError):
        return None


def set_cache(key: str, value: Any, ttl: int = CACHE_TTL_SECONDS) -> None:
    client = get_redis_client()
    if client is None:
        return
    try:
        client.setex(key, ttl, json.dumps(value, default=str))
    except redis.RedisError:
        return


def delete_cache(key: str) -> None:
    client = get_redis_client()
    if client is None:
        return
    try:
        client.delete(key)
    except redis.RedisError:
        return


def invalidate_earthquake_cache() -> None:
    """Clear cached earthquake list/detail responses."""
    client = get_redis_client()
    if client is None:
        return
    try:
        keys = list(client.scan_iter("earthquakes:*"))
        if keys:
            client.delete(*keys)
    except redis.RedisError:
        return
