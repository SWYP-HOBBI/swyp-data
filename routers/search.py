from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from database import get_db
from schemas.search import SearchRequest, SearchResults
from services.search_service import search_posts

router = APIRouter(prefix="/fastapi/v1/search", tags=["Search"])

@router.post("/", response_model=SearchResults)
def search_posts_endpoint(
    response: Response,
    req: SearchRequest,
    db: Session = Depends(get_db)
) -> SearchResults:
    """
    게시글 검색 API입니다.
    검색 조건과 바디의 cursor_created_at, cursor_id를 이용해 페이징합니다.
    """
    result = search_posts(db, req)

    # 응답 헤더에 다음 커서 정보 설정
    if result.next_cursor_created_at and result.next_cursor_post_id:
        response.headers["X-Next-Cursor-Created-At"] = result.next_cursor_created_at.isoformat()
        response.headers["X-Next-Cursor-Post-Id"]    = str(result.next_cursor_post_id)
        response.headers["X-Has-More"]               = str(result.has_more).lower()

    return result