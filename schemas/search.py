# schemas/search.py
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

# 게시글 응답 모델 (검색 결과 목록의 각 항목)
class PostResponse(BaseModel):
    postId: int
    userId: int
    nickname: str
    userImageUrl: Optional[str]
    title: str
    content: Optional[str]
    createdAt: datetime
    updatedAt: datetime
    commentCount: int = 0
    likeCount: int = 0
    postImageUrls: List[str] = []
    postHobbyTags: List[str] = []
    matchedFields: List[str]   # 어디에서 만났는지?: "제목+내용" / "작성자"

    class Config:
        from_attributes = True


# 검색 요청 본문 모델 (커서 기반 무한 스크롤)
class SearchRequest(BaseModel):
    keyword_user: Optional[str] = None  # 제목 + 내용
    keyword_text: Optional[str] = None  # 작성자(닉네임)
    mbti: Optional[List[str]] = None  # MBTI 목록 (예: ["I", "N", "T", "P"]) - 서비스/ES 로직에 따라 AND 조건으로 간주
    hobby_tags: Optional[List[str]] = None  # 취미 태그 목록 (예: [축구, 헬스]) - 서비스/ES 로직에 따라 OR 조건으로 간주
    cursor_created_at: Optional[datetime] = None  # 무한 스크롤 커서: 이전 페이지 마지막 게시글의 생성 시각
    cursor_id: Optional[int] = None  # 무한 스크롤 커서: 이전 페이지 마지막 게시글의 ID
    limit: int = 15  # 한 페이지에 가져올 게시글 수 (기본값 15)
    
    class Config:
        # 클라이언트에서 정확한 필드 이름(keyword_text, keyword_user)을 써야 합니다.
        from_attributes = True    # 기존 설정 예시
        populate_by_name = True   # v2용 새 옵션




# 검색 결과 응답 모델
class SearchResults(BaseModel):
    posts: List[PostResponse] # 검색된 게시글 목록
    next_cursor_created_at: Optional[datetime] # 다음 페이지 요청 시 사용할 커서 (생성 시각)
    next_cursor_post_id: Optional[int] # 다음 페이지 요청 시 사용할 커서 (게시글 ID)
    has_more: bool # 다음 페이지 결과가 더 있는지 여부
