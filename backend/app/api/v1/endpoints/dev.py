from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.db.seed import seed_database
from backend.app.cache.cache_manager import get_cache_dependency
from backend.app.cache.cache_interface import BaseCache
from backend.app.core.config import settings

router = APIRouter()

@router.post("/dev/seed", summary="Development-Only Database Seeding")
def dev_seed(
    force: bool = False,
    db: Session = Depends(get_db)
):
    if not settings.DEBUG:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Development seed endpoint is disabled in production environments."
        )
    seed_database(db, force=force)
    return {"status": "success", "message": "Development database seeded successfully."}

@router.post("/dev/cache-clear", summary="Development Cache Invalidation")
async def dev_cache_clear(
    cache: BaseCache = Depends(get_cache_dependency)
):
    if not settings.DEBUG:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cache clear endpoint is disabled in production."
        )
    await cache.delete_pattern("*")
    return {"status": "success", "message": "Cache invalidated."}
