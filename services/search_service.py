# services/search_service.py
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc
from typing import List, Tuple, Optional
from datetime import datetime
import logging

from models import post as post_model
from models import post_comment as comment_model
from models import post_hobby_tag as post_hobby_tag_model
from models.user import User as user_model
from models.hobby_tag import HobbyTag  # 태그명 → ID 변환용

from elastic.es_client import search_post_ids_from_es
from schemas.search import SearchRequest, SearchResults, PostResponse

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def search_posts(db: Session, req: SearchRequest) -> SearchResults:
    """
    통합 검색 서비스 함수 (제목+내용 ES 검색 + 작성자 SQL 검색 + SQL 필터 + 커서 기반 페이징)
    """

    # 1) ES로 "제목+내용" 검색한 post_id 리스트
    text_matched_ids: List[int] = []
    if req.keyword_text:
        text_matched_ids = search_post_ids_from_es(
            keyword=req.keyword_text,
            fields=["post_title", "post_content"],
            limit=req.limit
        )

    # 2) SQL로 "작성자(닉네임)" 검색한 post_id 리스트
    author_matched_ids: List[int] = []
    if req.keyword_user:
        rows = (
            db.query(post_model.Post.post_id)
              .join(post_model.Post.user)
              .filter(user_model.nickname.ilike(f"%{req.keyword_user}%"))
              .limit(req.limit)
              .all()
        )
        author_matched_ids = [r[0] for r in rows]

    # 3) matched_ids 결정 (AND 연산)
    if req.keyword_text and req.keyword_user:
        matched_ids = list(set(text_matched_ids) & set(author_matched_ids))
    elif req.keyword_text:
        matched_ids = text_matched_ids
    elif req.keyword_user:
        matched_ids = author_matched_ids
    else:
        matched_ids = None  # 키워드 검색 없으면 전체

    logger.info(f"text_matched_ids: {text_matched_ids}")
    logger.info(f"author_matched_ids: {author_matched_ids}")
    logger.info(f"matched_ids: {matched_ids}")

    # 4) 매치 없으면 빈 결과
    if matched_ids is not None and not matched_ids:
        return SearchResults(posts=[], next_cursor_created_at=None,
                             next_cursor_post_id=None, has_more=False)

    # 5) 댓글 수 서브쿼리
    comment_count_sq = (
        db.query(
            comment_model.PostComment.post_id,
            func.count(comment_model.PostComment.comment_id).label("comment_count")
        )
        .group_by(comment_model.PostComment.post_id)
        .subquery()
    )

    # 6) 메인 쿼리 구성
    query = (
        db.query(
            post_model.Post,
            comment_count_sq.c.comment_count
        )
        .outerjoin(comment_count_sq, post_model.Post.post_id == comment_count_sq.c.post_id)
        .options(
            joinedload(post_model.Post.user),
            joinedload(post_model.Post.images),
            joinedload(post_model.Post.like_count),
            joinedload(post_model.Post.post_hobby_tags)
                  .joinedload(post_hobby_tag_model.PostHobbyTag.hobby_tag),
        )
    )

    # 7) matched_ids 필터
    if matched_ids is not None:
        query = query.filter(post_model.Post.post_id.in_(matched_ids))

    # 8) MBTI 필터
    if req.mbti:
        mbti_str = "".join(req.mbti).upper()
        pattern = f"%{mbti_str}%" if len(mbti_str) == 1 else f"{mbti_str}%"
        query = (
            query
            .join(post_model.Post.user)
            .filter(user_model.mbti.ilike(pattern))
        )

    # 9) Hobby 태그명 → ID 변환 + 필터
    if req.hobby_tags:
        # 문자열 목록을 ID 목록으로 변환
        tag_rows = (
            db.query(HobbyTag.hobby_tag_id)
              .filter(HobbyTag.hobby_tag_name.in_(req.hobby_tags))
              .all()
        )
        hobby_tag_ids = [r[0] for r in tag_rows]
        if hobby_tag_ids:
            query = (
                query
                .join(
                    post_hobby_tag_model.PostHobbyTag,
                    post_model.Post.post_id == post_hobby_tag_model.PostHobbyTag.post_id
                )
                .filter(post_hobby_tag_model.PostHobbyTag.hobby_tag_id.in_(hobby_tag_ids))
            )

    # 10) 커서 페이징: 최신순 정렬 + limit+1
    rows: List[Tuple[post_model.Post, int]] = (
        query.order_by(
            desc(post_model.Post.created_at),
            desc(post_model.Post.post_id)
        )
        .limit(req.limit + 1)
        .all()
    )

    has_more = len(rows) > req.limit
    if has_more:
        last_post, _ = rows[-1]
        next_cursor_created_at = last_post.created_at
        next_cursor_post_id = last_post.post_id
        rows = rows[:-1]
    else:
        next_cursor_created_at = None
        next_cursor_post_id = None

    # 11) 직렬화
    post_items: List[PostResponse] = []
    for post, comment_count in rows:
        matched_fields: List[str] = []
        if req.keyword_text and post.post_id in text_matched_ids:
            matched_fields.append("제목+내용")
        if req.keyword_user and post.post_id in author_matched_ids:
            matched_fields.append("작성자")

        post_items.append(
            PostResponse(
                postId=post.post_id,
                userId=post.user_id,
                nickname=post.user.nickname,
                userImageUrl=post.user.user_image_url,
                title=post.post_title,
                content=post.post_content,
                createdAt=post.created_at,
                updatedAt=post.updated_at,
                commentCount=comment_count or 0,
                likeCount=post.like_count.like_count if post.like_count else 0,
                postImageUrls=[img.image_url for img in post.images],
                postHobbyTags=[tag.hobby_tag.hobby_tag_name for tag in post.post_hobby_tags],
                matchedFields=matched_fields,
            )
        )

    return SearchResults(
        posts=post_items,
        next_cursor_created_at=next_cursor_created_at,
        next_cursor_post_id=next_cursor_post_id,
        has_more=has_more
    )