from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.db.session import get_db
from backend.app.cache.cache_manager import get_cache_dependency
from backend.app.cache.cache_interface import BaseCache
from backend.app.core.config import settings
import datetime

router = APIRouter()

@router.get("/health", summary="System Health Check")
async def health_check(
    db: Session = Depends(get_db),
    cache: BaseCache = Depends(get_cache_dependency)
):
    # Check Database
    db_status = "healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    # Check Cache
    cache_ping = await cache.ping()
    cache_type = "Redis" if settings.REDIS_ENABLED and cache_ping else "In-Memory Fallback"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "services": {
            "database": {
                "status": db_status,
                "engine": "sqlite" if settings.DATABASE_URL.startswith("sqlite") else "postgresql"
            },
            "cache": {
                "status": "connected" if cache_ping else "error",
                "backend": cache_type
            },
            "messaging": {
                "status": "active",
                "backend": "Kafka" if settings.KAFKA_ENABLED else "Local Async Queue"
            }
        }
    }
