from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
from backend.app.models.interaction import Interaction

class InteractionRepository:
    def __init__(self, db: Session):
        self.db = db

    def record_interaction(self, user_id: int, article_id: int, interaction_type: str) -> Interaction:
        interaction = Interaction(
            user_id=user_id,
            article_id=article_id,
            interaction_type=interaction_type,
            created_at=datetime.utcnow()
        )
        self.db.add(interaction)
        self.db.commit()
        return interaction

    def get_user_interactions(self, user_id: int, limit: int = 50) -> List[Interaction]:
        return (
            self.db.query(Interaction)
            .filter(Interaction.user_id == user_id)
            .order_by(Interaction.created_at.desc())
            .limit(limit)
            .all()
        )
