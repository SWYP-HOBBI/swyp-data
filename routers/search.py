from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db # 데이터베이스 세션 의존성 주입
from schemas.search import SearchRequest, SearchResults,PostResponse # 정의한 스키마 임포트
from services.search_service import search_posts # 서비스 함수 임포트
from typing import List


router = APIRouter(prefix="/fastapi/v1/search", tags=["Search"])

# POST 메소드로 정의하며, 요청 본문은 SearchRequest, 응답 모델은 SearchResults
# @router.post("/", response_model=List[PostResponse]) 
# 리스트
@router.post("/", response_model=SearchResults) 
# 딕셔너리
def search_posts_endpoint(req: SearchRequest, db: Session = Depends(get_db)):
    """
    게시글 검색 API 엔드포인트입니다.
    요청 본문에 검색 조건 (키워드, MBTI, 태그)과 무한 스크롤 커서 정보를 받아 검색 결과를 반환합니다.
    """
    # 서비스 계층의 search_posts 함수를 호출하여 검색 결과를 가져옵니다.
    search_result = search_posts(db, req)
    return search_result