from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.models.base import Base

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(500), nullable=False, index=True)
    description = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    source = Column(String(150), nullable=False, index=True)
    author = Column(String(150), nullable=True)
    image_url = Column(String(1000), nullable=True)
    published_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    region = Column(String(10), default="GLOBAL", index=True, nullable=False)
    view_count = Column(Integer, default=0, nullable=False, index=True)
    engagement_count = Column(Integer, default=0, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    topics = relationship("ArticleTopic", back_populates="article", cascade="all, delete-orphan")
    interactions = relationship("Interaction", back_populates="article", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="article", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_article_region_trending", "region", "view_count", "published_at"),
        Index("idx_article_published", "published_at"),
    )

class ArticleTopic(Base):
    __tablename__ = "article_topics"

    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), primary_key=True)

    article = relationship("Article", back_populates="topics")
    topic = relationship("Topic", back_populates="article_topics")
