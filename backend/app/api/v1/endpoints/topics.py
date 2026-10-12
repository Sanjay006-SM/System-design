from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from backend.app.db.session import get_db
from backend.app.services.topic_service import TopicService
from backend.app.schemas.topic import TopicResponse

router = APIRouter()

@router.get("/topics", response_model=List[TopicResponse], summary="Get All Topics")
def get_topics(db: Session = Depends(get_db)):
    service = TopicService(db, None)
    topics = service.get_all_topics()
    return [TopicResponse.model_validate(t) for t in topics]
