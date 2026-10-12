from fastapi import APIRouter, Depends, Path, BackgroundTasks
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.cache.cache_manager import get_cache_dependency
from backend.app.cache.cache_interface import BaseCache
from backend.app.services.article_service import ArticleService
from backend.app.schemas.article import ArticleDetailResponse

router = APIRouter()

@router.get("/articles/{articleId}", summary="Get Article Details")
async def get_article_details(
    articleId: int = Path(..., ge=1, description="Unique Article ID"),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    cache: BaseCache = Depends(get_cache_dependency)
):
    service = ArticleService(db, cache)
    return await service.get_article_details(articleId, background_tasks=background_tasks)
