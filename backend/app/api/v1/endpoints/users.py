from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.db.session import get_db
from backend.app.cache.cache_manager import get_cache_dependency
from backend.app.cache.cache_interface import BaseCache
from backend.app.services.topic_service import TopicService
from backend.app.services.feed_service import PersonalizedFeedService
from backend.app.services.notification_service import NotificationService
from backend.app.repositories.user_repo import UserRepository
from backend.app.schemas.topic import (
    FollowTopicRequest,
    FollowTopicResponse,
    UnfollowTopicResponse,
    TopicResponse,
)
from backend.app.schemas.user import UserResponse, DemoLoginRequest, TokenResponse
from backend.app.schemas.notification import NotificationListResponse
from backend.app.core.security import create_access_token
from backend.app.core.exceptions import ResourceNotFoundException

router = APIRouter()

@router.get("/users", response_model=List[UserResponse], summary="List Demo Users")
def list_demo_users(db: Session = Depends(get_db)):
    users = db.query(UserRepository(db).get_by_id(101)._sa_instance_state.class_).all()
    result = []
    topic_service = TopicService(db, None)
    for u in users:
        followed = topic_service.get_user_topics(u.id)
        result.append(UserResponse(
            id=u.id,
            username=u.username,
            email=u.email,
            created_at=u.created_at,
            followed_topics=[TopicResponse.model_validate(t) for t in followed]
        ))
    return result

@router.post("/auth/demo-login", response_model=TokenResponse, summary="Demo Login for MVP Authentication")
def demo_login(
    payload: DemoLoginRequest,
    db: Session = Depends(get_db)
):
    user_repo = UserRepository(db)
    user = user_repo.get_by_username(payload.username)
    if not user:
        raise ResourceNotFoundException("User", payload.username)

    token = create_access_token(user_id=user.id, username=user.username)
    topic_service = TopicService(db, None)
    followed = topic_service.get_user_topics(user.id)
    
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            created_at=user.created_at,
            followed_topics=[TopicResponse.model_validate(t) for t in followed]
        )
    )

@router.post(
    "/users/{userId}/topics",
    response_model=FollowTopicResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Follow Topic"
)
async def follow_topic(
    payload: FollowTopicRequest,
    userId: int = Path(..., ge=1, description="User ID"),
    db: Session = Depends(get_db),
    cache: BaseCache = Depends(get_cache_dependency)
):
    service = TopicService(db, cache)
    result = await service.follow_topic(user_id=userId, topic_id=payload.topicId)
    return result

@router.delete(
    "/users/{userId}/topics/{topicId}",
    response_model=UnfollowTopicResponse,
    summary="Unfollow Topic"
)
async def unfollow_topic(
    userId: int = Path(..., ge=1, description="User ID"),
    topicId: int = Path(..., ge=1, description="Topic ID"),
    db: Session = Depends(get_db),
    cache: BaseCache = Depends(get_cache_dependency)
):
    service = TopicService(db, cache)
    result = await service.unfollow_topic(user_id=userId, topic_id=topicId)
    return result

@router.get(
    "/users/{userId}/topics",
    response_model=List[TopicResponse],
    summary="Get Topics Followed by User"
)
def get_user_topics(
    userId: int = Path(..., ge=1, description="User ID"),
    db: Session = Depends(get_db),
    cache: BaseCache = Depends(get_cache_dependency)
):
    service = TopicService(db, cache)
    return service.get_user_topics(user_id=userId)

@router.get(
    "/users/{userId}/feed",
    summary="Get Personalized Feed"
)
async def get_personalized_feed(
    userId: int = Path(..., ge=1, description="User ID"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    cache: BaseCache = Depends(get_cache_dependency)
):
    service = PersonalizedFeedService(db, cache)
    return await service.get_user_feed(user_id=userId, page=page, limit=limit)

@router.get(
    "/users/{userId}/notifications",
    response_model=NotificationListResponse,
    summary="Get User Notifications"
)
def get_user_notifications(
    userId: int = Path(..., ge=1, description="User ID"),
    status: Optional[str] = Query(None, description="Optional status filter: 'unread' or 'read'"),
    db: Session = Depends(get_db)
):
    service = NotificationService(db)
    return service.get_notifications(user_id=userId, status_filter=status)

@router.post(
    "/users/{userId}/notifications/{notificationId}/read",
    summary="Mark Notification as Read"
)
def mark_notification_read(
    userId: int = Path(..., ge=1, description="User ID"),
    notificationId: int = Path(..., ge=1, description="Notification ID"),
    db: Session = Depends(get_db)
):
    service = NotificationService(db)
    success = service.mark_notification_as_read(userId, notificationId)
    if not success:
        raise ResourceNotFoundException("Notification", notificationId)
    return {"status": "success", "message": "Notification marked as read"}

@router.post(
    "/users/{userId}/notifications/mark-all-read",
    summary="Mark All Notifications as Read"
)
def mark_all_notifications_read(
    userId: int = Path(..., ge=1, description="User ID"),
    db: Session = Depends(get_db)
):
    service = NotificationService(db)
    count = service.mark_all_as_read(userId)
    return {"status": "success", "marked_read_count": count}
