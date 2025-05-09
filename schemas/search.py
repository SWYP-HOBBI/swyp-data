from typing import List, Optional
from pydantic import BaseModel

class SearchRequest(BaseModel):
    mbti: Optional[List[str]] = None  # 예: ["i", "s", "t"]
    hobby_tags: Optional[List[int]] = None  # hobby_tag_id 리스트
    keyword: Optional[str] = None  # Elasticsearch용 키워드
    page: int = 1
    size: int = 15
