from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc
from typing import Optional, List, Tuple
from datetime import datetime
from models import post as post_model
from models import post_comment as comment_model
from models import post_hobby_tag as post_hobby_tag_model
from schemas import post as post_schema


def get_posts_by_cursor(
    db: Session,
    cursor_created_at: Optional[datetime],
    cursor_id: Optional[int],
    limit: int = 15
) -> Tuple[List[post_schema.PostList], Optional[datetime], Optional[int], bool]:

    # 댓글 수 서브쿼리
    comment_count_subquery = (
        db.query(
            comment_model.PostComment.post_id,
            func.count(comment_model.PostComment.comment_id).label("comment_count")
        )
        .group_by(comment_model.PostComment.post_id)
        .subquery()
    )

    # 기본 쿼리 작성
    query = (
        db.query(
            post_model.Post,
            comment_count_subquery.c.comment_count
        )
        .outerjoin(comment_count_subquery, post_model.Post.post_id == comment_count_subquery.c.post_id)
        .options(
            joinedload(post_model.Post.user),
            joinedload(post_model.Post.images),
            joinedload(post_model.Post.like_count),
            joinedload(post_model.Post.post_hobby_tags).joinedload(post_hobby_tag_model.PostHobbyTag.hobby_tag),
        )
    )

    # 커서 기반 필터링 먼저 적용
    if cursor_id:
        query = query.filter(post_model.Post.post_id < cursor_id)

    # 정렬 및 제한 적용
    query = query.order_by(desc(post_model.Post.created_at), desc(post_model.Post.post_id)).limit(limit + 1)

    # 쿼리 실행
    posts = query.all()

    # has_more 플래그 계산 및 다음 커서 설정
    has_more = len(posts) > limit
    next_cursor_created_at = None
    next_cursor_post_id = None

    if has_more:
        next_cursor_post = posts[-1]
        next_cursor_created_at = next_cursor_post[0].created_at
        next_cursor_post_id = next_cursor_post[0].post_id
        posts = posts[:-1]

    # 결과 데이터 생성
    post_list = [
        post_schema.PostList(
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
        ) for post, comment_count in posts
    ]

    return post_list, next_cursor_created_at, next_cursor_post_id, has_more


# 특정 게시물 조회
def get_post(db: Session, post_id: int) -> Optional[post_schema.PostDetail]:
    
    post = (
        db.query(post_model.Post)
        .filter(post_model.Post.post_id == post_id)
        .options(
            joinedload(post_model.Post.user),
            joinedload(post_model.Post.images),
            joinedload(post_model.Post.like_count),
            joinedload(post_model.Post.post_hobby_tags).joinedload(post_hobby_tag_model.PostHobbyTag.hobby_tag),
            joinedload(post_model.Post.comments).joinedload(comment_model.PostComment.user) 
        )
        .first()
    )

    if post:
        # 댓글 수 계산
        comment_count = (
            db.query(func.count(comment_model.PostComment.comment_id))
            .filter(comment_model.PostComment.post_id == post_id)
            .scalar() or 0
        )

        # 반환 객체 생성
        return post_schema.PostDetail(
            postId=post.post_id,
            userId=post.user_id,
            nickname=post.user.nickname if post.user else "Unknown",
            userImageUrl=post.user.user_image_url if post.user else None,
            title=post.post_title,
            content=post.post_content,
            createdAt=post.created_at,
            updatedAt=post.updated_at,
            commentCount=comment_count,
            likeCount=post.like_count.like_count if post.like_count else 0,
            postImageUrls=[img.image_url for img in post.images],
            postHobbyTags=[tag.hobby_tag.hobby_tag_name for tag in post.post_hobby_tags],
            comments=[
                post_schema.PostComment(
                    comment_id=comment.comment_id,
                    user_id=comment.user_id,
                    nickname=comment.user.nickname if comment.user else "Unknown",
                    post_id=comment.post_id,  # post_id는 이미 comment 모델에 존재함
                    parent_comment_id=comment.parent_comment_id,  # parent_comment_id는 Optional로 처리됨
                    comment_content=comment.comment_content,  # comment_content 필드로 수정
                    created_at=comment.created_at,
                    updated_at=comment.updated_at
                )
                for comment in post.comments
            ]
        )
    
    return None
# 댓글 무한 스크롤 
def get_post_comments_by_cursor(
    db: Session,
    post_id: int,
    cursor_comment_id: Optional[int],
    limit: int = 15) -> Tuple[List[post_schema.PostComment], Optional[int], bool]:

    query = (
        db.query(comment_model.PostComment)
        .filter(comment_model.PostComment.post_id == post_id)
        .options(joinedload(comment_model.PostComment.user))
    )

    if cursor_comment_id:
        query = query.filter(comment_model.PostComment.comment_id < cursor_comment_id)

    comments = query.order_by(desc(comment_model.PostComment.comment_id)).limit(limit + 1).all()

    has_more = len(comments) > limit
    next_cursor_comment_id = None

    if has_more:
        next_cursor_comment_id = comments[-1].comment_id
        comments = comments[:-1]

    comment_list = [
        post_schema.PostComment(
            comment_id=comment.comment_id,
            user_id=comment.user_id,
            nickname=comment.user.nickname if comment.user else "Unknown",
            post_id=comment.post_id,
            parent_comment_id=comment.parent_comment_id,
            comment_content=comment.comment_content,
            created_at=comment.created_at,
            updated_at=comment.updated_at
        )
        for comment in comments
    ]

    return comment_list, next_cursor_comment_id, has_more