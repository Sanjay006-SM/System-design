import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from backend.app.repositories.topic_repo import TopicRepository
from backend.app.repositories.user_repo import UserRepository
from backend.app.cache.cache_interface import BaseCache
from backend.app.core.exceptions import ResourceNotFoundException, ResourceConflictException
from backend.app.messaging import get_event_bus
from backend.app.schemas.event import TopicFollowedEvent
import uuid

logger = logging.getLogger("service.topic")

class TopicService:
    def __init__(self, db: Session, cache: BaseCache):
        self.db = db
        self.cache = cache
        self.topic_repo = TopicRepository(db)
        self.user_repo = UserRepository(db)

    def get_all_topics(self):
        return self.topic_repo.get_all()

    def get_user_topics(self, user_id: int):
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundException("User", user_id)
        return self.topic_repo.get_user_topics(user_id)

    async def follow_topic(self, user_id: int, topic_id: int) -> Dict[str, Any]:
        # 1. Validate user
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundException("User", user_id)

        # 2. Validate topic
        topic = self.topic_repo.get_by_id(topic_id)
        if not topic:
            raise ResourceNotFoundException("Topic", topic_id)

        # 3. Check for existing follow (prevent duplicate / return 409 Conflict)
        if self.topic_repo.is_following(user_id, topic_id):
            raise ResourceConflictException(
                f"User {user_id} is already following topic '{topic.name}'"
            )

        try:
            self.topic_repo.follow_topic(user_id, topic_id)
        except IntegrityError:
            self.db.rollback()
            raise ResourceConflictException(
                f"User {user_id} is already following topic '{topic.name}'"
            )

        # 4. Invalidate personalized feed caches for this user
        pattern = f"feed:user:{user_id}:*"
        await self.cache.delete_pattern(pattern)
        logger.info(f"Invalidated feed cache pattern '{pattern}' for user {user_id}")

        # 5. Publish event
        event_bus = get_event_bus()
        await event_bus.publish(
            "topic.events",
            TopicFollowedEvent(
                event_id=str(uuid.uuid4()),
                user_id=user_id,
                topic_id=topic_id,
                topic_name=topic.name
            )
        )

        return {
            "userId": user_id,
            "topicId": topic_id,
            "topicName": topic.name,
            "status": "followed"
        }

    async def unfollow_topic(self, user_id: int, topic_id: int) -> Dict[str, Any]:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundException("User", user_id)

        topic = self.topic_repo.get_by_id(topic_id)
        if not topic:
            raise ResourceNotFoundException("Topic", topic_id)

        success = self.topic_repo.unfollow_topic(user_id, topic_id)
        if not success:
            raise ResourceNotFoundException("Topic follow relationship", f"{user_id}->{topic_id}")

        # Invalidate feed cache
        pattern = f"feed:user:{user_id}:*"
        await self.cache.delete_pattern(pattern)
        logger.info(f"Invalidated feed cache pattern '{pattern}' after unfollow for user {user_id}")

        return {
            "userId": user_id,
            "topicId": topic_id,
            "status": "unfollowed",
            "message": f"Successfully unfollowed '{topic.name}'"
        }
