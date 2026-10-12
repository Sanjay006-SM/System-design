import logging
from typing import Optional
from backend.app.core.config import settings
from backend.app.cache.cache_interface import BaseCache
from backend.app.cache.memory_cache import InMemoryCache
from backend.app.cache.redis_cache import RedisCache

logger = logging.getLogger("cache.manager")

class CacheManager:
    _instance: Optional[BaseCache] = None

    @classmethod
    async def get_cache(cls) -> BaseCache:
        if cls._instance is None:
            if settings.REDIS_ENABLED:
                try:
                    redis_client = RedisCache(settings.REDIS_URL)
                    if await redis_client.ping():
                        logger.info("Connected to Redis cache backend.")
                        cls._instance = redis_client
                        return cls._instance
                    else:
                        logger.warning("Redis ping failed, falling back to In-Memory cache.")
                except Exception as e:
                    logger.warning(f"Failed to connect to Redis: {e}. Falling back to In-Memory cache.")
            
            logger.info("Using In-Memory Cache backend.")
            cls._instance = InMemoryCache()
            
        return cls._instance

async def get_cache_dependency() -> BaseCache:
    return await CacheManager.get_cache()
