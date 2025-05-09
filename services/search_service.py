from sqlalchemy.orm import Session
from typing import List, Optional
from models.post import Post
from models.user import User
from models.post_hobby_tag import PostHobbyTag
from models.post_comment import PostComment
from schemas.search import SearchRequest
from elastic.es_client import search_posts_by_keyword

def search_posts(db: Session, req: SearchRequest):
    query = db.query(Post).join(User).outerjoin(PostHobbyTag).outerjoin(PostComment)

    # MBTI 필터링
    if req.mbti:
        for trait in req.mbti:
            query = query.filter(User.mbti.ilike(f"%{trait}%"))

    # 태그 필터링
    if req.hobby_tags:
        query = query.filter(PostHobbyTag.hobby_tag_id.in_(req.hobby_tags))

    # 키워드로 검색(엘라스틱 서치)
    post_ids_from_es = None
    if req.keyword:
        post_ids_from_es = search_posts_by_keyword(req.keyword)
        if post_ids_from_es:
            query = query.filter(Post.post_id.in_(post_ids_from_es))

    # 페이지네이션
    offset = (req.page - 1) * req.size
    query = query.distinct().order_by(Post.created_at.desc()).offset(offset).limit(req.size)

    return query.all()
