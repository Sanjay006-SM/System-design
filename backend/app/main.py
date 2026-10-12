import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.core.exceptions import (
    AppException,
    app_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    generic_exception_handler
)
from backend.app.db.session import init_db, SessionLocal
from backend.app.db.seed import seed_database
from backend.app.messaging import get_event_bus
from backend.app.services.notification_service import NotificationService
from backend.app.api.v1.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up Personalized News & Information Platform...")
    init_db()
    
    # Auto-seed initial sample data for immediate developer/evaluator experience
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

    # Start Event Bus and register Notification worker
    event_bus = get_event_bus()
    event_bus.subscribe("article.published", NotificationService.handle_article_published_event)
    await event_bus.start()

    yield

    # Shutdown
    logger.info("Shutting down platform...")
    await event_bus.stop()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Scalable Personalized News & Information Platform with Cache-Aside Caching, Full-Text Search, and Event-Driven Notifications.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware for React/Vite development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Request latency logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    logger.info(
        f"{request.method} {request.url.path} completed with status {response.status_code} in {process_time:.2f}ms"
    )
    return response

# Mount API v1 router
app.include_router(api_router, prefix="/api/v1")

@app.get("/", summary="Root Health / Info")
def root_info():
    return {
        "platform": settings.PROJECT_NAME,
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }
