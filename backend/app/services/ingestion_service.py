import logging
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from backend.app.repositories.article_repo import ArticleRepository
from backend.app.repositories.topic_repo import TopicRepository
from backend.app.models.article import Article
from backend.app.schemas.event import NewArticlePublishedEvent
from backend.app.messaging import get_event_bus
from backend.app.core.config import settings

logger = logging.getLogger("service.ingestion")

class NewsIngestionService:
    def __init__(self, db: Session):
        self.db = db
        self.article_repo = ArticleRepository(db)
        self.topic_repo = TopicRepository(db)

    async def ingest_article(
        self,
        title: str,
        description: str,
        content: str,
        source: str,
        author: Optional[str] = None,
        image_url: Optional[str] = None,
        region: str = "GLOBAL",
        topic_names: List[str] = None,
        published_at: Optional[datetime] = None,
        is_live_external: bool = False
    ) -> Optional[Article]:
        # 1. Deduplication check: title + source
        existing = (
            self.db.query(Article)
            .filter(Article.title == title.strip(), Article.source == source.strip())
            .first()
        )
        if existing:
            logger.info(f"Skipping duplicate article: '{title}' from '{source}'")
            return existing

        # 2. Resolve or create topics
        topic_ids = []
        resolved_topic_names = []
        if topic_names:
            for tname in topic_names:
                slug = tname.lower().replace(" ", "-").replace("&", "and")
                topic = self.topic_repo.get_by_slug(slug)
                if not topic:
                    topic = self.topic_repo.create(name=tname, slug=slug)
                topic_ids.append(topic.id)
                resolved_topic_names.append(topic.name)

        # 3. Persist article
        article = self.article_repo.create(
            title=title.strip(),
            description=description.strip(),
            content=content.strip(),
            source=f"{source} (Live)" if is_live_external else source,
            author=author,
            image_url=image_url,
            region=region,
            topic_ids=topic_ids,
            published_at=published_at or datetime.utcnow()
        )

        # 4. Publish NewArticlePublished event
        event = NewArticlePublishedEvent(
            event_id=str(uuid.uuid4()),
            article_id=article.id,
            title=article.title,
            summary=article.description[:200],
            topic_ids=topic_ids,
            topic_names=resolved_topic_names,
            author=article.author,
            source=article.source,
            region=article.region
        )

        event_bus = get_event_bus()
        await event_bus.publish("article.published", event)
        logger.info(f"Published NewArticlePublished event for Article {article.id}")

        return article
