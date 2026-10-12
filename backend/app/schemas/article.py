from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from backend.app.schemas.topic import TopicResponse

class ArticleBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=500)
    description: str
    content: str
    source: str
    author: Optional[str] = None
    image_url: Optional[str] = None
    region: str = "GLOBAL"

class ArticleCreate(ArticleBase):
    topic_ids: List[int] = []

class ArticleResponse(ArticleBase):
    id: int
    published_at: datetime
    view_count: int
    engagement_count: int
    created_at: datetime
    topics: List[TopicResponse] = []

    class Config:
        from_attributes = True

class ArticleDetailResponse(ArticleResponse):
    pass

class PaginatedArticlesResponse(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int
    items: List[ArticleResponse]
