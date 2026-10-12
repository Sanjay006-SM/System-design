from typing import Optional, List
from sqlalchemy.orm import Session
from backend.app.models.user import User
from backend.app.models.topic import UserTopic

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def create(self, username: str, email: str) -> User:
        user = User(username=username, email=email)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_followed_topic_ids(self, user_id: int) -> List[int]:
        user_topics = self.db.query(UserTopic).filter(UserTopic.user_id == user_id).all()
        return [ut.topic_id for ut in user_topics]
