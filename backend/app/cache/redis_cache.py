import json
import logging
from typing import Optional, Any
from redis.asyncio import Redis, from_url
from redis.exceptions import RedisError
from backend.app.cache.cache_interface import BaseCache

logger = logging.getLogger("cache.redis")

class RedisCache(BaseCache):
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self._client: Optional[Redis] = None

    async def _get_client(self) -> Redis:
        if self._client is None:
            self._client = from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=2.0
            )
        return self._client

    async def get(self, key: str) -> Optional[Any]:
        try:
            client = await self._get_client()
            val = await client.get(key)
            if val is not None:
                return json.loads(val)
            return None
        except (RedisError, Exception) as e:
            logger.warning(f"Redis GET failed for key {key}: {e}. Falling back to miss.")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        try:
            client = await self._get_client()
            serialized = json.dumps(value)
            if ttl:
                await client.setex(key, ttl, serialized)
            else:
                await client.set(key, serialized)
            return True
        except (RedisError, Exception) as e:
            logger.warning(f"Redis SET failed for key {key}: {e}.")
            return False

    async def delete(self, key: str) -> bool:
        try:
            client = await self._get_client()
            await client.delete(key)
            return True
        except (RedisError, Exception) as e:
            logger.warning(f"Redis DELETE failed for key {key}: {e}.")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        try:
            client = await self._get_client()
            keys = await client.keys(pattern)
            if keys:
                return await client.delete(*keys)
            return 0
        except (RedisError, Exception) as e:
            logger.warning(f"Redis DELETE_PATTERN failed for pattern {pattern}: {e}.")
            return 0

    async def ping(self) -> bool:
        try:
            client = await self._get_client()
            return await client.ping()
        except Exception:
            return False

    async def close(self):
        if self._client:
            await self._client.close()
