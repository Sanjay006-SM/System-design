from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from backend.app.models.topic import Topic, UserTopic

class TopicRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Topic]:
        return self.db.query(Topic).order_by(Topic.name).all()

    def get_by_id(self, topic_id: int) -> Optional[Topic]:
        return self.db.query(Topic).filter(Topic.id == topic_id).first()

    def get_by_slug(self, slug: str) -> Optional[Topic]:
        return self.db.query(Topic).filter(Topic.slug == slug).first()

    def create(self, name: str, slug: str) -> Topic:
        topic = Topic(name=name, slug=slug)
        self.db.add(topic)
        self.db.commit()
        self.db.refresh(topic)
        return topic

    def get_user_topics(self, user_id: int) -> List[Topic]:
        return (
            self.db.query(Topic)
            .join(UserTopic, UserTopic.topic_id == Topic.id)
            .filter(UserTopic.user_id == user_id)
            .all()
        )

    def is_following(self, user_id: int, topic_id: int) -> bool:
        record = (
            self.db.query(UserTopic)
            .filter(UserTopic.user_id == user_id, UserTopic.topic_id == topic_id)
            .first()
        )
        return record is not None

    def follow_topic(self, user_id: int, topic_id: int) -> UserTopic:
        user_topic = UserTopic(user_id=user_id, topic_id=topic_id, followed_at=datetime.utcnow())
        self.db.add(user_topic)
        self.db.commit()
        return user_topic

    def unfollow_topic(self, user_id: int, topic_id: int) -> bool:
        record = (
            self.db.query(UserTopic)
            .filter(UserTopic.user_id == user_id, UserTopic.topic_id == topic_id)
            .first()
        )
        if record:
            self.db.delete(record)
            self.db.commit()
            return True
        return False

    def get_users_following_topic(self, topic_id: int) -> List[int]:
        records = self.db.query(UserTopic.user_id).filter(UserTopic.topic_id == topic_id).all()
        return [r[0] for r in records]
