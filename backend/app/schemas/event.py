from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

class EventBase(BaseModel):
    event_id: str
    event_type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0"

class NewArticlePublishedEvent(EventBase):
    event_type: str = "NewArticlePublished"
    article_id: int
    title: str
    summary: str
    topic_ids: List[int]
    topic_names: List[str]
    author: Optional[str] = None
    source: str
    region: str

class BreakingNewsDetectedEvent(EventBase):
    event_type: str = "BreakingNewsDetected"
    article_id: int
    title: str
    urgency_level: str = "high"
    region: str

class TopicFollowedEvent(EventBase):
    event_type: str = "TopicFollowed"
    user_id: int
    topic_id: int
    topic_name: str

class NotificationRequestedEvent(EventBase):
    event_type: str = "NotificationRequested"
    user_id: int
    article_id: Optional[int]
    message: str
