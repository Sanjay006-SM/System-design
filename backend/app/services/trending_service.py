import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from backend.app.repositories.article_repo import ArticleRepository
from backend.app.cache.cache_interface import BaseCache
from backend.app.core.config import settings

logger = logging.getLogger("service.trending")

class TrendingNewsService:
    def __init__(self, db: Session, cache: BaseCache):
        self.db = db
        self.cache = cache
        self.article_repo = ArticleRepository(db)

    async def get_trending_news(self, region: str = "GLOBAL", limit: int = 10) -> List[Dict[str, Any]]:
        normalized_region = (region or "GLOBAL").upper()
        cache_key = f"trending:{normalized_region}:limit:{limit}"

        # 1. Try cache
        try:
            cached_data = await self.cache.get(cache_key)
            if cached_data is not None:
                logger.info(f"Cache HIT for trending news '{cache_key}'")
                return cached_data
        except Exception as e:
            logger.warning(f"Cache lookup failed for {cache_key}: {e}. Proceeding to DB.")

        logger.info(f"Cache MISS for trending news '{cache_key}', querying database.")

        # 2. Query database with ranking
        articles = self.article_repo.get_trending(region=normalized_region, limit=limit)

        result = []
        for art in articles:
            result.append({
                "id": art.id,
                "title": art.title,
                "description": art.description,
                "content": art.content,
                "source": art.source,
                "author": art.author,
                "image_url": art.image_url,
                "published_at": art.published_at.isoformat() + "Z",
                "region": art.region,
                "view_count": art.view_count,
                "engagement_count": art.engagement_count,
                "created_at": art.created_at.isoformat() + "Z",
                "topics": [
                    {"id": at.topic.id, "name": at.topic.name, "slug": at.topic.slug}
                    for at in art.topics
                ]
            })

        # 3. Cache result
        try:
            await self.cache.set(cache_key, result, ttl=settings.CACHE_TTL_TRENDING)
        except Exception as e:
            logger.warning(f"Failed to set cache for {cache_key}: {e}")

        return result
