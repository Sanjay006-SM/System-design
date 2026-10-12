from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from datetime import datetime
from backend.app.models.notification import Notification

class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, message: str, article_id: Optional[int] = None) -> Notification:
        # Check if identical unread notification already exists to prevent duplicate spam
        existing = (
            self.db.query(Notification)
            .filter(
                Notification.user_id == user_id,
                Notification.article_id == article_id,
                Notification.message == message,
                Notification.status == "unread"
            )
            .first()
        )
        if existing:
            return existing

        notif = Notification(
            user_id=user_id,
            article_id=article_id,
            message=message,
            status="unread",
            created_at=datetime.utcnow()
        )
        self.db.add(notif)
        self.db.commit()
        self.db.refresh(notif)
        return notif

    def get_by_user_id(
        self, user_id: int, status_filter: Optional[str] = None, limit: int = 50
    ) -> Tuple[List[Notification], int, int]:
        query = self.db.query(Notification).filter(Notification.user_id == user_id)
        if status_filter:
            query = query.filter(Notification.status == status_filter)

        total = query.count()
        unread_count = (
            self.db.query(Notification)
            .filter(Notification.user_id == user_id, Notification.status == "unread")
            .count()
        )
        items = query.order_by(Notification.created_at.desc()).limit(limit).all()
        return items, total, unread_count

    def mark_all_as_read(self, user_id: int) -> int:
        updated = (
            self.db.query(Notification)
            .filter(Notification.user_id == user_id, Notification.status == "unread")
            .update({Notification.status: "read"})
        )
        self.db.commit()
        return updated

    def mark_as_read(self, user_id: int, notification_id: int) -> bool:
        record = (
            self.db.query(Notification)
            .filter(Notification.user_id == user_id, Notification.id == notification_id)
            .first()
        )
        if record:
            record.status = "read"
            self.db.commit()
            return True
        return False
