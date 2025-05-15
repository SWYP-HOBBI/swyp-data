# models/post.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import Column, BigInteger, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from database import Base

class Post(Base):
    __tablename__ = 'post'

    post_id      = Column(BigInteger, primary_key=True)
    user_id      = Column(BigInteger, ForeignKey("user.user_id"), nullable=False)
    post_title   = Column(Text, nullable=False)
    post_content = Column(Text)
    created_at   = Column(DateTime, nullable=False)
    updated_at   = Column(DateTime, nullable=False)

    # 관계 설정
    user            = relationship("User", back_populates="posts")
    comments        = relationship("PostComment", back_populates="post")
    images          = relationship("PostImage", back_populates="post")
    likes           = relationship("PostLike", back_populates="post")

    # 좋아요 개수를 위한 1:1 매핑
    like_count      = relationship(
        "PostLikeCount",
        uselist=False,
        back_populates="post",
        lazy="joined"
    )

    # 댓글 개수
    comment_count   = relationship(
        "PostCommentCount",
        back_populates="post",
        uselist=False,
        lazy="joined"
    )
    post_tags       = relationship(
        "PostHobbyTag",
        back_populates="post",
        cascade="all, delete-orphan",
        overlaps="post_hobby_tags"
    )
    post_hobby_tags = relationship(
        "PostHobbyTag",
        back_populates="post",
        overlaps="post_tags"
    )

    @property
    def comment_count_value(self):
        return self.comment_count.comment_count if self.comment_count else 0

    @property
    def like_count_value(self):
        # PostLikeCount.like_count 값 반환 (없으면 0)
        return self.like_count.like_count if self.like_count else 0

    @classmethod
    def get_related_models(cls):
        from . import (
            user,
            post_comment,
            post_like,
            post_like_count,
            post_hobby_tag,
            post_comment_count
        )
        return (
            user,
            post_comment,
            post_like,
            post_like_count,
            post_hobby_tag,
            post_comment_count
        )