from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TopicBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100)

class TopicCreate(TopicBase):
    pass

class TopicResponse(TopicBase):
    id: int

    class Config:
        from_attributes = True

class FollowTopicRequest(BaseModel):
    topicId: int = Field(..., description="ID of the topic to follow")

class FollowTopicResponse(BaseModel):
    userId: int
    topicId: int
    topicName: str
    status: str = "followed"

class UnfollowTopicResponse(BaseModel):
    userId: int
    topicId: int
    status: str = "unfollowed"
    message: str = "Successfully unfollowed topic"
