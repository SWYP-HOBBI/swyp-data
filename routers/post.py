# from fastapi import APIRouter, Depends, Query
# from sqlalchemy.orm import Session
# from typing import List, Optional
# from datetime import datetime
# from database import get_db
# from schemas import post as post_schema
# from services import post_service

# router = APIRouter(
#     prefix="/fastapi/v1/posts",
#     tags=["posts"]
# )

# # 포스트 목록 조회 (커서 기반)
# @router.get("/", response_model=List[post_schema.PostList])
# def read_posts(
#     cursorCreatedAt: Optional[datetime] = Query(None, alias="cursor_created_at"),
#     cursorId: Optional[int] = Query(None, alias="cursor_id"),
#     limit: int = Query(15),
#     db: Session = Depends(get_db)
# ):
#     posts, next_cursor_created_at, next_cursor_post_id = post_service.get_posts_by_cursor(
#         db, cursorCreatedAt, cursorId, limit
#     )

#     # 응답에 커서 정보도 함께 반환
#     return {
#         "posts": posts,
#         "next_cursor_created_at": next_cursor_created_at,
#         "next_cursor_post_id": next_cursor_post_id,
#     }

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from database import get_db
from schemas import post as post_schema
from services import post_service

router = APIRouter(
    prefix="/fastapi/v1/posts",
    tags=["posts"]
)
@router.get("/", response_model=List[post_schema.PostList])
def read_posts(
    response: Response,
    cursor_created_at: Optional[datetime] = Query(None, alias="cursor_created_at"),
    cursor_post_id: Optional[int] = Query(None, alias="cursor_post_id"),
    limit: int = Query(15),
    db: Session = Depends(get_db)
):
    # 서비스 함수에서 게시물 목록과 다음 커서 정보를 함께 받음
    # 4개의 리턴 값을 모두 받도록 수정
    posts, next_cursor_created_at, next_cursor_post_id, has_more = post_service.get_posts_by_cursor(
        db, cursor_created_at, cursor_post_id, limit
    )

    if next_cursor_post_id:
        response.headers["X-Next-Cursor-Post-Id"] = str(next_cursor_post_id)
        response.headers["X-Has-More"] = str(has_more).lower()

    return posts
    # # 응답 모델에 맞게 데이터 구조화
    # return post_schema.PostListResponse(
    #     items=posts,
    #     next_cursor_created_at=next_cursor_created_at,
    #     next_cursor_post_id=next_cursor_post_id
    # )
#포스트 목록 조회 (커서 기반) - /cursor 경로 추가
@router.get("/cursor", response_model=List[post_schema.PostList])
def read_posts_by_cursor(
    response: Response,
    cursor_created_at: Optional[datetime] = Query(None, alias="cursor_created_at"),
    cursor_id: Optional[int] = Query(None, alias="cursor_id"),
    limit: int = Query(15),
    db: Session = Depends(get_db)
):
    posts, next_cursor_created_at, next_cursor_post_id, has_more = post_service.get_posts_by_cursor(
        db, cursor_created_at, cursor_id, limit
    )

    if next_cursor_post_id:
        response.headers["X-Next-Cursor-Post-Id"] = str(next_cursor_post_id)
        response.headers["X-Has-More"] = str(has_more).lower()

    return posts

    # if next_cursor_created_at and next_cursor_post_id:
    #     response.headers["X-Next-Cursor-Created-At"] = str(next_cursor_created_at)
    #     response.headers["X-Next-Cursor-Post-Id"] = str(next_cursor_post_id)
    
    # return posts


# @router.get("/cursor")
# def read_posts_by_cursor(
#     cursorCreatedAt: Optional[datetime] = Query(None, alias="cursor_created_at"),
#     cursorId: Optional[int] = Query(None, alias="cursor_id"),
#     limit: int = Query(15),
#     db: Session = Depends(get_db)
# ):
#     # 커서가 없는 경우, 첫 페이지로 간주
#     if not cursorCreatedAt or not cursorId:
#         cursorCreatedAt = None
#         cursorId = None

#     posts, next_cursor_created_at, next_cursor_post_id, has_more = post_service.get_posts_by_cursor(
#     db, cursorCreatedAt, cursorId, limit
#     )   

#     return {
#     "posts": posts,
#     "next_cursor": {
#         "created_at": next_cursor_created_at,
#         "post_id": next_cursor_post_id
#     },
#     "has_more": has_more
# }
    # # next_cursor 구조로 반환
    # next_cursor = {
    #     "created_at": next_cursor_created_at,
    #     "post_id": next_cursor_post_id,
    # }

    # return {
    #     "posts": posts,
    #     "next_cursor": next_cursor
    # }

# 특정 포스트 조회 (상세 정보 포함)
@router.get("/{post_id}", response_model=post_schema.PostDetail)
def read_post(post_id: int, db: Session = Depends(get_db)):
    return post_service.get_post(db, post_id)


# 특정 포스트의 댓글 목록 조회 (커서 기반)
@router.get("/{post_id}/comments", response_model=List[post_schema.PostComment])
def read_post_comments_by_cursor(
    response: Response,
    post_id: int,
    cursor_comment_id: Optional[int] = Query(None, alias="cursor_comment_id"),
    limit: int = Query(15),
    db: Session = Depends(get_db)
):
    comments, next_cursor_comment_id, has_more = post_service.get_post_comments_by_cursor(
        db, post_id, cursor_comment_id, limit
    )

    if next_cursor_comment_id:
        response.headers["X-Next-Cursor-Comment-Id"] = str(next_cursor_comment_id)
        response.headers["X-Has-More"] = str(has_more).lower()

    return comments