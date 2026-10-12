import pytest
import asyncio
from fastapi import status
from backend.app.schemas.event import NewArticlePublishedEvent
from backend.app.services.notification_service import NotificationService
from backend.app.repositories.notification_repo import NotificationRepository
from backend.app.repositories.topic_repo import TopicRepository

def test_health_check(client):
    res = client.get("/api/v1/health")
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert "status" in data
    assert "services" in data
    assert data["services"]["database"]["status"] == "healthy"

def test_search_articles_success(client):
    res = client.get("/api/v1/news/search?q=AI&page=1&limit=5")
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert "total" in data
    assert data["total"] > 0
    assert data["page"] == 1
    assert data["limit"] == 5
    assert len(data["items"]) <= 5
    assert "title" in data["items"][0]
    assert "topics" in data["items"][0]

def test_search_validation_empty_query(client):
    res = client.get("/api/v1/news/search?q=")
    assert res.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]

def test_get_existing_article(client):
    # Search first to get a real ID
    search_res = client.get("/api/v1/news/search?q=Quantum&page=1&limit=1")
    article_id = search_res.json()["items"][0]["id"]

    res = client.get(f"/api/v1/articles/{article_id}")
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data["id"] == article_id
    assert "title" in data
    assert "content" in data
    assert "view_count" in data
    assert len(data["topics"]) > 0

def test_get_unknown_article_returns_404(client):
    res = client.get("/api/v1/articles/999999")
    assert res.status_code == status.HTTP_404_NOT_FOUND
    assert "error" in res.json()

def test_follow_topic_success_and_duplicate_rejection(client):
    # User 104 starts with no followed topics
    # Topic 1 is Artificial Intelligence
    res = client.post("/api/v1/users/104/topics", json={"topicId": 1})
    assert res.status_code == status.HTTP_201_CREATED
    data = res.json()
    assert data["userId"] == 104
    assert data["topicId"] == 1
    assert data["status"] == "followed"
    assert "topicName" in data

    # Attempting to follow again must return 409 Conflict
    dup_res = client.post("/api/v1/users/104/topics", json={"topicId": 1})
    assert dup_res.status_code == status.HTTP_409_CONFLICT
    assert "already following" in dup_res.json()["error"]["message"].lower()

def test_follow_unknown_topic_returns_404(client):
    res = client.post("/api/v1/users/104/topics", json={"topicId": 99999})
    assert res.status_code == status.HTTP_404_NOT_FOUND

def test_unfollow_topic_success_and_error(client):
    # Follow first
    client.post("/api/v1/users/104/topics", json={"topicId": 2})

    # Unfollow
    res = client.delete("/api/v1/users/104/topics/2")
    assert res.status_code == status.HTTP_200_OK
    assert res.json()["status"] == "unfollowed"

    # Unfollowing again returns 404
    res2 = client.delete("/api/v1/users/104/topics/2")
    assert res2.status_code == status.HTTP_404_NOT_FOUND

def test_personalized_feed_ranked_and_fallback(client):
    # User 101 follows AI, Technology, Cybersecurity in seed data
    res = client.get("/api/v1/users/101/feed?page=1&limit=5")
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data["user_id"] == 101
    assert data["has_followed_topics"] is True
    assert len(data["items"]) > 0

    # User 104 follows no topics -> returns sensible default feed
    res_default = client.get("/api/v1/users/104/feed?page=1&limit=5")
    assert res_default.status_code == status.HTTP_200_OK
    data_default = res_default.json()
    assert data_default["user_id"] == 104
    assert data_default["has_followed_topics"] is False
    assert len(data_default["items"]) > 0

def test_trending_news(client):
    res = client.get("/api/v1/news/trending?region=GLOBAL&limit=5")
    assert res.status_code == status.HTTP_200_OK
    items = res.json()
    assert isinstance(items, list)
    assert len(items) <= 5
    assert len(items) > 0
    # Highest view/engagement counts should rank first
    first_rank_score = items[0]["view_count"] * 1.0 + items[0]["engagement_count"] * 2.5
    last_rank_score = items[-1]["view_count"] * 1.0 + items[-1]["engagement_count"] * 2.5
    assert first_rank_score >= last_rank_score

def test_get_all_topics(client):
    res = client.get("/api/v1/topics")
    assert res.status_code == status.HTTP_200_OK
    topics = res.json()
    assert len(topics) >= 10
    assert any(t["slug"] == "artificial-intelligence" for t in topics)

@pytest.mark.asyncio
async def test_notification_creation_on_event(db_session):
    # User 101 follows topic 1 (Artificial Intelligence)
    topic_repo = TopicRepository(db_session)
    ai_topic = topic_repo.get_by_slug("artificial-intelligence")
    followers = topic_repo.get_users_following_topic(ai_topic.id)
    assert 101 in followers

    event = NewArticlePublishedEvent(
        event_id="evt-test-123",
        article_id=999,
        title="Breaking Neural Supercomputing Framework Released",
        summary="Major open architecture announcement.",
        topic_ids=[ai_topic.id],
        topic_names=[ai_topic.name],
        source="ArXiv Test",
        region="GLOBAL"
    )

    # Process event through handler
    await NotificationService.handle_article_published_event(event)

    # Check notification persisted
    notif_repo = NotificationRepository(db_session)
    items, total, unread = notif_repo.get_by_user_id(101)
    assert any(n.article_id == 999 for n in items)
