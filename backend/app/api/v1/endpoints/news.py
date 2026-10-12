from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from backend.app.db.session import get_db
from backend.app.cache.cache_manager import get_cache_dependency
from backend.app.cache.cache_interface import BaseCache
from backend.app.services.article_service import ArticleService
from backend.app.services.trending_service import TrendingNewsService
from backend.app.services.ingestion_service import NewsIngestionService
from backend.app.schemas.article import PaginatedArticlesResponse, ArticleResponse, ArticleCreate
from pydantic import BaseModel

router = APIRouter()

class PublishNewsRequest(BaseModel):
    title: str
    description: str
    content: str
    source: str
    author: Optional[str] = None
    image_url: Optional[str] = None
    region: str = "GLOBAL"
    topic_names: List[str] = []

@router.get("/news/search", response_model=PaginatedArticlesResponse, summary="Search News Articles")
async def search_news(
    q: str = Query(..., min_length=1, description="Search keyword for titles, descriptions, and topics"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    cache: BaseCache = Depends(get_cache_dependency)
):
    service = ArticleService(db, cache)
    return service.search_news(query=q, page=page, limit=limit)

@router.get("/news/trending", summary="Get Trending News")
async def get_trending_news(
    region: str = Query("GLOBAL", description="Geographic region code, e.g., IN, US, GLOBAL"),
    limit: int = Query(10, ge=1, le=50, description="Max trending articles to return"),
    db: Session = Depends(get_db),
    cache: BaseCache = Depends(get_cache_dependency)
):
    service = TrendingNewsService(db, cache)
    return await service.get_trending_news(region=region, limit=limit)

@router.post("/news/publish", status_code=status.HTTP_201_CREATED, summary="Publish New Article (Triggers Event Flow)")
async def publish_news(
    payload: PublishNewsRequest,
    db: Session = Depends(get_db)
):
    ingestion = NewsIngestionService(db)
    article = await ingestion.ingest_article(
        title=payload.title,
        description=payload.description,
        content=payload.content,
        source=payload.source,
        author=payload.author,
        image_url=payload.image_url,
        region=payload.region,
        topic_names=payload.topic_names
    )
    return {
        "status": "published",
        "article_id": article.id,
        "title": article.title,
        "event_published": True,
        "message": "Article published and NewArticlePublished event broadcasted."
    }
