from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class PostCreate(BaseModel):
    post_title: str
    post_content: Optional[str] = None

class PostUpdate(BaseModel):
    post_title: Optional[str] = None
    post_content: Optional[str] = None

class PostImage(BaseModel):
    image_id: int
    post_id: int
    image_file_name: str
    image_url: Optional[str] = "default_image_path"  # Changed to `image_url` based on your DB model

    class Config:
        from_attributes = True

class PostViewCount(BaseModel):
    view_count: int

    class Config:
        from_attributes = True

class PostLikeCount(BaseModel):
    like_count: int

    class Config:
        from_attributes = True

class HobbyTag(BaseModel):
    hobby_tag_id: int
    hobby_tag_name: str
    hobby_type: str

    class Config:
        from_attributes = True


class PostList(BaseModel):
    postId: int
    userId: int
    nickname: Optional[str] = None
    userImageUrl: Optional[str] = None
    title: str
    createdAt: datetime
    updatedAt: datetime
    content: Optional[str] = None
    commentCount: Optional[int] = 0
    likeCount: Optional[int] = 0
    postImageUrls: List[str] = []
    postHobbyTags: List[str] = []

    class Config:
        from_attributes = True
        
class CursorResponse(BaseModel):
    posts: List[PostList]
    next_cursor: Optional[dict]
    has_more: bool

class Post(BaseModel):
    postId: int
    userId: int
    nickname: Optional[str] = None
    userImageUrl: Optional[str] = None
    title: str
    content: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime
    commentCount: Optional[int] = 0
    likeCount: Optional[int] = 0
    postImageUrls: List[str] = []
    postHobbyTags: List[str] = []

    class Config:
        orm_mode = True  # SQLAlchemy ORM 객체를 Pydantic 모델로 변환


class PostComment(BaseModel):
    comment_id: int
    user_id: int
    nickname: str
    post_id: int
    parent_comment_id: Optional[int] = None
    comment_content: str  # Optional을 제거하고 필수로 처리
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True  # SQLAlchemy ORM 객체를 Pydantic 모델로 변환


class PostDetail(Post):
    comments: List[PostComment] = []  # 기본값을 빈 리스트로 설정

    class Config:
        orm_mode = True  # SQLAlchemy ORM 객체를 Pydantic 모델로 변환  

class PostListResponse(BaseModel):
    items: List[PostList]
    next_cursor_created_at: Optional[datetime] = None
    next_cursor_post_id: Optional[int] = None
    
    class Config:
        from_attributes = True


class Cursor(BaseModel):
    createdAt: datetime
    postId: int

class PostCursorResponse(BaseModel):
    results: List[PostList]  # Use PostList for post listings
    nextCursor: Optional[Cursor]
