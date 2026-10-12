from fastapi import APIRouter
from backend.app.api.v1.endpoints import news, articles, topics, users, health, dev

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(news.router, tags=["News"])
api_router.include_router(articles.router, tags=["Articles"])
api_router.include_router(topics.router, tags=["Topics"])
api_router.include_router(users.router, tags=["Users"])
api_router.include_router(dev.router, tags=["Development"])
