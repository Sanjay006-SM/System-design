from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.models.base import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=True, index=True)
    message = Column(String(500), nullable=False)
    status = Column(String(20), default="unread", index=True, nullable=False)  # "unread", "read"
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = relationship("User", back_populates="notifications")
    article = relationship("Article", back_populates="notifications")

    __table_args__ = (
        Index("idx_notification_user_unread", "user_id", "status", "created_at"),
    )
