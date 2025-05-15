from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc, or_, and_
from typing import List, Optional
from datetime import datetime
import logging

from models import post as post_model
from models import post_comment as comment_model
from models import post_hobby_tag as post_hobby_tag_model
from models.user import User as user_model
from models.hobby_tag import HobbyTag
from elastic.es_client import search_post_ids_from_es
from schemas.search import SearchRequest, SearchResults, PostResponse

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def search_posts(db: Session, req: SearchRequest) -> SearchResults:
    # 1) ES 제목+내용 검색
    text_ids: List[int] = []
    if req.keyword_text:
        text_ids = search_post_ids_from_es(
            keyword=req.keyword_text,
            fields=["post_title", "post_content"],
            limit=req.limit
        )

    # 2) 작성자 검색
    author_ids: List[int] = []
    if req.keyword_user:
        rows = (
            db.query(post_model.Post.post_id)
              .join(post_model.Post.user)
              .filter(user_model.nickname.ilike(f"%{req.keyword_user}%"))
              .limit(req.limit)
              .all()
        )
        author_ids = [r[0] for r in rows]

    # 3) matched_ids 결정 (ES 결과가 있을 때만 사용)
    if req.keyword_text and req.keyword_user:
        matched_ids = list(set(text_ids) & set(author_ids))
    elif req.keyword_text:
        matched_ids = text_ids if text_ids else None  
        # ↑ ES(text_ids)가 비어 있으면 None으로 두고, SQL ILIKE 페일백만 동작하게 함
    elif req.keyword_user:
        matched_ids = author_ids
    else:
        matched_ids = None

    # 4) ES+작성자 검색 조합 시, 둘 다 검색했는데 매치가 하나도 없으면 빈 결과
    if matched_ids is not None and not matched_ids:
        return SearchResults(posts=[], next_cursor_created_at=None,
                             next_cursor_post_id=None, has_more=False)

    # 5) 댓글 수 서브쿼리
    cc_sub = (
        db.query(
            comment_model.PostComment.post_id,
            func.count(comment_model.PostComment.comment_id).label("comment_count")
        )
        .group_by(comment_model.PostComment.post_id)
        .subquery()
    )

    # 6) 기본 쿼리 작성
    query = (
        db.query(post_model.Post, cc_sub.c.comment_count)
          .outerjoin(cc_sub, post_model.Post.post_id == cc_sub.c.post_id)
          .options(
              joinedload(post_model.Post.user),
              joinedload(post_model.Post.images),
              joinedload(post_model.Post.like_count),
              joinedload(post_model.Post.post_hobby_tags)
                    .joinedload(post_hobby_tag_model.PostHobbyTag.hobby_tag),
          )
    )
    if req.keyword_text:
        query = query.filter(
            or_(
                post_model.Post.post_title.ilike(f"%{req.keyword_text}%"),
                post_model.Post.post_content.ilike(f"%{req.keyword_text}%")
            )
        )

    # 7) 매치 ID 필터
    if matched_ids is not None:
        query = query.filter(post_model.Post.post_id.in_(matched_ids))
        

    # 8) MBTI 필터
    if req.mbti:
        mbti_str = "".join(req.mbti).upper()
        pattern = f"%{mbti_str}%" if len(mbti_str)==1 else f"{mbti_str}%"
        query = (
            query
            .join(post_model.Post.user)
            .filter(user_model.mbti.ilike(pattern))
        )

    # 9) 취미 태그 필터
    if req.hobby_tags:
        tags = [r[0] for r in db.query(HobbyTag.hobby_tag_id)
                                 .filter(HobbyTag.hobby_tag_name.in_(req.hobby_tags)).all()]
        if tags:
            query = (
                query
                .join(post_hobby_tag_model.PostHobbyTag,
                      post_model.Post.post_id == post_hobby_tag_model.PostHobbyTag.post_id)
                .filter(post_hobby_tag_model.PostHobbyTag.hobby_tag_id.in_(tags))
            )

    # 10) 커서 필터링
    if req.cursor_created_at and req.cursor_id:
        query = query.filter(
            or_(
                post_model.Post.created_at < req.cursor_created_at,
                and_(
                    post_model.Post.created_at == req.cursor_created_at,
                    post_model.Post.post_id < req.cursor_id
                )
            )
        )
    elif req.cursor_id:
        query = query.filter(post_model.Post.post_id < req.cursor_id)

    # 11) 정렬 + limit+1
    items = query.order_by(
        desc(post_model.Post.created_at), desc(post_model.Post.post_id)
    ).limit(req.limit + 1).all()

    # 12) has_more 및 다음 커서 추출
    has_more = len(items) > req.limit
    if has_more:
        last, _ = items[-1]
        next_created = last.created_at
        next_id      = last.post_id
        items        = items[:-1]
    else:
        next_created = None
        next_id      = None

    # 13) 직렬화
    posts = []
    for post, count in items:
        matched = []

        # keyword_text가 있으면 ES든 SQL ILIKE 페일백이든 제목/본문에서 매치된 것으로 간주
        if req.keyword_text:
            matched.append("제목+내용")

        if req.keyword_user and post.post_id in author_ids:
            matched.append("작성자")

        if req.mbti:
            matched.append("MBTI")

        if req.hobby_tags and post.post_hobby_tags:
            matched.append("태그")

        posts.append(
            PostResponse(
                postId=post.post_id,
                userId=post.user_id,
                nickname=post.user.nickname,
                userImageUrl=post.user.user_image_url,
                title=post.post_title,
                content=post.post_content,
                createdAt=post.created_at,
                updatedAt=post.updated_at,
                commentCount=count or 0,
                likeCount=post.like_count.like_count if post.like_count else 0,
                postImageUrls=[i.image_url for i in post.images],
                postHobbyTags=[t.hobby_tag.hobby_tag_name for t in post.post_hobby_tags],
                matchedFields=matched,
            )
        )

    # 14) 최종 결과 반환
    return SearchResults(
        posts=posts,
        next_cursor_created_at=next_created,
        next_cursor_post_id=next_id,
        has_more=has_more
    )