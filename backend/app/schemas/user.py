from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
from backend.app.schemas.topic import TopicResponse

class UserBase(BaseModel):
    username: str = Field(..., min_length=2, max_length=100)
    email: EmailStr

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    created_at: datetime
    followed_topics: List[TopicResponse] = []

    class Config:
        from_attributes = True

class DemoLoginRequest(BaseModel):
    username: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
