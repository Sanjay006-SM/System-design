import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from backend.app.repositories.notification_repo import NotificationRepository
from backend.app.repositories.topic_repo import TopicRepository
from backend.app.schemas.event import NewArticlePublishedEvent
from backend.app.db.session import SessionLocal

logger = logging.getLogger("service.notification")

class NotificationService:
    def __init__(self, db: Session):
        self.db = db
        self.notif_repo = NotificationRepository(db)
        self.topic_repo = TopicRepository(db)

    def get_notifications(self, user_id: int, status_filter: str = None) -> Dict[str, Any]:
        items, total, unread_count = self.notif_repo.get_by_user_id(user_id, status_filter)
        return {
            "total": total,
            "unread_count": unread_count,
            "items": [
                {
                    "id": n.id,
                    "user_id": n.user_id,
                    "article_id": n.article_id,
                    "message": n.message,
                    "status": n.status,
                    "created_at": n.created_at.isoformat() + "Z"
                }
                for n in items
            ]
        }

    def mark_notification_as_read(self, user_id: int, notification_id: int) -> bool:
        return self.notif_repo.mark_as_read(user_id, notification_id)

    def mark_all_as_read(self, user_id: int) -> int:
        return self.notif_repo.mark_all_as_read(user_id)

    @staticmethod
    async def handle_article_published_event(event: NewArticlePublishedEvent):
        """
        Asynchronous event worker handler for 'NewArticlePublished'.
        Finds users following the article's topics and creates personalized notifications.
        """
        logger.info(f"Notification worker processing event for Article ID {event.article_id}: '{event.title}'")
        db = SessionLocal()
        try:
            topic_repo = TopicRepository(db)
            notif_repo = NotificationRepository(db)

            # Collect unique user IDs who follow any of the article's topics
            users_to_notify = set()
            for topic_id in event.topic_ids:
                followers = topic_repo.get_users_following_topic(topic_id)
                users_to_notify.update(followers)

            logger.info(f"Found {len(users_to_notify)} users to notify for article {event.article_id}")

            topic_summary = ", ".join(event.topic_names[:2]) if event.topic_names else "news"
            message = f"New story in {topic_summary}: '{event.title}'"

            # Create in-app notification for each user
            created_count = 0
            for user_id in users_to_notify:
                try:
                    notif_repo.create(
                        user_id=user_id,
                        message=message,
                        article_id=event.article_id
                    )
                    created_count += 1
                except Exception as inner_e:
                    logger.error(f"Failed to create notification for user {user_id}: {inner_e}")

            logger.info(f"Successfully generated {created_count} notifications for article {event.article_id}")
        except Exception as e:
            logger.exception(f"Error in handle_article_published_event: {e}")
        finally:
            db.close()
