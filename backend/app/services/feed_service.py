import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from backend.app.repositories.article_repo import ArticleRepository
from backend.app.repositories.user_repo import UserRepository
from backend.app.cache.cache_interface import BaseCache
from backend.app.core.config import settings
from backend.app.core.exceptions import ResourceNotFoundException, BadRequestException

logger = logging.getLogger("service.feed")

class PersonalizedFeedService:
    def __init__(self, db: Session, cache: BaseCache):
        self.db = db
        self.cache = cache
        self.article_repo = ArticleRepository(db)
        self.user_repo = UserRepository(db)

    async def get_user_feed(
        self, user_id: int, page: int = 1, limit: int = 10
    ) -> Dict[str, Any]:
        if page < 1:
            raise BadRequestException("Page must be >= 1")
        if limit < 1 or limit > 100:
            raise BadRequestException("Limit must be between 1 and 100")

        # 1. Verify user exists
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundException("User", user_id)

        cache_key = f"feed:user:{user_id}:page:{page}:limit:{limit}"

        # 2. Check cache
        try:
            cached_data = await self.cache.get(cache_key)
            if cached_data is not None:
                logger.info(f"Cache HIT for user feed '{cache_key}'")
                return cached_data
        except Exception as e:
            logger.warning(f"Cache lookup failed for {cache_key}: {e}. Proceeding to DB.")

        logger.info(f"Cache MISS for user feed '{cache_key}', generating feed.")

        # 3. Retrieve followed topic IDs
        followed_topic_ids = self.user_repo.get_followed_topic_ids(user_id)

        # 4. Fetch ranked articles (or default feed if user follows no topics)
        articles, total = self.article_repo.get_feed_by_topic_ids(
            topic_ids=followed_topic_ids,
            page=page,
            limit=limit
        )

        items = []
        for art in articles:
            items.append({
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

        total_pages = (total + limit - 1) // limit if total > 0 else 1

        feed_response = {
            "user_id": user_id,
            "has_followed_topics": len(followed_topic_ids) > 0,
            "followed_topics_count": len(followed_topic_ids),
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "items": items
        }

        # 5. Cache response
        try:
            await self.cache.set(cache_key, feed_response, ttl=settings.CACHE_TTL_FEED)
        except Exception as e:
            logger.warning(f"Failed to set cache for {cache_key}: {e}")

        return feed_response
