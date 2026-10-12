from typing import Optional, List, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, desc, func, distinct
from backend.app.models.article import Article, ArticleTopic
from backend.app.models.topic import Topic

class ArticleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, article_id: int) -> Optional[Article]:
        return (
            self.db.query(Article)
            .options(joinedload(Article.topics).joinedload(ArticleTopic.topic))
            .filter(Article.id == article_id)
            .first()
        )

    def search_articles(
        self, query: str, page: int = 1, limit: int = 10
    ) -> Tuple[List[Article], int]:
        offset = (page - 1) * limit
        search_pattern = f"%{query}%"

        # Search titles, descriptions, and associated topics
        base_query = (
            self.db.query(Article)
            .outerjoin(ArticleTopic, Article.id == ArticleTopic.article_id)
            .outerjoin(Topic, ArticleTopic.topic_id == Topic.id)
            .filter(
                or_(
                    Article.title.ilike(search_pattern),
                    Article.description.ilike(search_pattern),
                    Topic.name.ilike(search_pattern),
                    Topic.slug.ilike(search_pattern),
                )
            )
            .distinct()
        )

        total = base_query.count()
        articles = (
            base_query.options(joinedload(Article.topics).joinedload(ArticleTopic.topic))
            .order_by(desc(Article.published_at))
            .offset(offset)
            .limit(limit)
            .all()
        )
        return articles, total

    def increment_view_count(self, article_id: int):
        self.db.query(Article).filter(Article.id == article_id).update(
            {Article.view_count: Article.view_count + 1}
        )
        self.db.commit()

    def increment_engagement_count(self, article_id: int, amount: int = 1):
        self.db.query(Article).filter(Article.id == article_id).update(
            {Article.engagement_count: Article.engagement_count + amount}
        )
        self.db.commit()

    def get_trending(self, region: str = "GLOBAL", limit: int = 10) -> List[Article]:
        """
        Ranks news using recency, views, and engagement.
        Ranking formula: (views * 1.0 + engagement * 2.5) / (recency_decay_factor)
        """
        query = self.db.query(Article)
        if region and region != "GLOBAL":
            query = query.filter(or_(Article.region == region, Article.region == "GLOBAL"))

        articles = (
            query.options(joinedload(Article.topics).joinedload(ArticleTopic.topic))
            .order_by(
                desc(Article.view_count * 1.0 + Article.engagement_count * 2.5),
                desc(Article.published_at)
            )
            .limit(limit)
            .all()
        )
        return articles

    def get_feed_by_topic_ids(
        self, topic_ids: List[int], page: int = 1, limit: int = 10
    ) -> Tuple[List[Article], int]:
        offset = (page - 1) * limit
        
        if not topic_ids:
            # Fallback to general recent/engaging feed
            base_query = self.db.query(Article)
            total = base_query.count()
            articles = (
                base_query.options(joinedload(Article.topics).joinedload(ArticleTopic.topic))
                .order_by(desc(Article.published_at), desc(Article.view_count))
                .offset(offset)
                .limit(limit)
                .all()
            )
            return articles, total

        # Personalized query matching followed topic IDs
        base_query = (
            self.db.query(Article)
            .join(ArticleTopic, Article.id == ArticleTopic.article_id)
            .filter(ArticleTopic.topic_id.in_(topic_ids))
            .distinct()
        )

        total = base_query.count()
        articles = (
            base_query.options(joinedload(Article.topics).joinedload(ArticleTopic.topic))
            .order_by(
                desc(Article.published_at),
                desc(Article.engagement_count * 2 + Article.view_count)
            )
            .offset(offset)
            .limit(limit)
            .all()
        )
        return articles, total

    def create(
        self,
        title: str,
        description: str,
        content: str,
        source: str,
        author: Optional[str] = None,
        image_url: Optional[str] = None,
        region: str = "GLOBAL",
        topic_ids: List[int] = None,
        published_at: Optional[datetime] = None
    ) -> Article:
        article = Article(
            title=title,
            description=description,
            content=content,
            source=source,
            author=author,
            image_url=image_url,
            region=region,
            published_at=published_at or datetime.utcnow()
        )
        self.db.add(article)
        self.db.flush()

        if topic_ids:
            for tid in topic_ids:
                self.db.add(ArticleTopic(article_id=article.id, topic_id=tid))

        self.db.commit()
        return self.get_by_id(article.id)
