from backend.app.models.base import Base
from backend.app.models.user import User
from backend.app.models.topic import Topic, UserTopic
from backend.app.models.article import Article, ArticleTopic
from backend.app.models.interaction import Interaction
from backend.app.models.notification import Notification

__all__ = [
    "Base",
    "User",
    "Topic",
    "UserTopic",
    "Article",
    "ArticleTopic",
    "Interaction",
    "Notification"
]
