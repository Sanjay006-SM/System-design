import logging
from typing import Optional, Dict, Any, Tuple, List
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks
from backend.app.repositories.article_repo import ArticleRepository
from backend.app.cache.cache_interface import BaseCache
from backend.app.core.config import settings
from backend.app.core.exceptions import ResourceNotFoundException, BadRequestException
from backend.app.db.session import SessionLocal

logger = logging.getLogger("service.article")

def _record_view_background(article_id: int):
    """Executes asynchronous view count incrementing on a dedicated session"""
    db = SessionLocal()
    try:
        repo = ArticleRepository(db)
        repo.increment_view_count(article_id)
        logger.info(f"Recorded background view for article {article_id}")
    except Exception as e:
        logger.error(f"Failed to record view for article {article_id}: {e}")
    finally:
        db.close()

class ArticleService:
    def __init__(self, db: Session, cache: BaseCache):
        self.db = db
        self.cache = cache
        self.article_repo = ArticleRepository(db)

    async def get_article_details(
        self, article_id: int, background_tasks: Optional[BackgroundTasks] = None
    ) -> Dict[str, Any]:
        # Cache-aside lookup
        cache_key = f"article:{article_id}"
        cached_data = await self.cache.get(cache_key)

        article = self.article_repo.get_by_id(article_id)
        if not article:
            raise ResourceNotFoundException("Article", article_id)

        # Trigger background view count tracking without blocking response
        if background_tasks:
            background_tasks.add_task(_record_view_background, article_id)
        else:
            self.article_repo.increment_view_count(article_id)

        # Serialize topics
        topics_list = [
            {"id": at.topic.id, "name": at.topic.name, "slug": at.topic.slug}
            for at in article.topics
        ]

        article_dict = {
            "id": article.id,
            "title": article.title,
            "description": article.description,
            "content": article.content,
            "source": article.source,
            "author": article.author,
            "image_url": article.image_url,
            "published_at": article.published_at.isoformat() + "Z",
            "region": article.region,
            "view_count": article.view_count + 1,  # reflects current view
            "engagement_count": article.engagement_count,
            "created_at": article.created_at.isoformat() + "Z",
            "topics": topics_list
        }

        # Cache with configurable TTL
        await self.cache.set(cache_key, article_dict, ttl=settings.CACHE_TTL_ARTICLE)
        return article_dict

    def search_news(
        self, query: str, page: int = 1, limit: int = 10
    ) -> Dict[str, Any]:
        if not query or len(query.strip()) == 0:
            raise BadRequestException("Search query 'q' cannot be empty")

        if page < 1:
            raise BadRequestException("Page must be >= 1")
        if limit < 1 or limit > 100:
            raise BadRequestException("Limit must be between 1 and 100")

        articles, total = self.article_repo.search_articles(query.strip(), page=page, limit=limit)
        
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

        return {
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "items": items
        }
