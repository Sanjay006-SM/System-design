from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.models.base import Base

class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)

    # Relationships
    article_topics = relationship("ArticleTopic", back_populates="topic", cascade="all, delete-orphan")
    followers = relationship("UserTopic", back_populates="topic", cascade="all, delete-orphan")

class UserTopic(Base):
    __tablename__ = "user_topics"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), primary_key=True)
    followed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "topic_id", name="uq_user_topic"),
    )

    user = relationship("User", back_populates="followed_topics")
    topic = relationship("Topic", back_populates="followers")
