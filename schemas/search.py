from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class SearchRequest(BaseModel):
    keyword_text: Optional[str] = None
    keyword_user: Optional[str] = None
    mbti: Optional[List[str]] = None
    hobby_tags: Optional[List[str]] = None
    limit: int = 15

    # 무한스크롤용 커서 필드
    cursor_created_at: Optional[datetime] = Field(None, alias="cursor_created_at")
    cursor_id: Optional[int] = Field(None, alias="cursor_id")

    class Config:
        populate_by_name = True
        from_attributes = True

class PostResponse(BaseModel):
    postId: int
    userId: int
    nickname: Optional[str]
    userImageUrl: Optional[str]
    title: str
    content: Optional[str]
    createdAt: datetime
    updatedAt: datetime
    commentCount: int
    likeCount: int
    postImageUrls: List[str]
    postHobbyTags: List[str]
    matchedFields: List[str]

    class Config:
        from_attributes = True

class SearchResults(BaseModel):
    posts: List[PostResponse]
    next_cursor_created_at: Optional[datetime] = None
    next_cursor_post_id: Optional[int] = None
    has_more: bool

    class Config:
        from_attributes = True