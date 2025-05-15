import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import Column, BigInteger, String, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from database import Base

class Post(Base):
    __tablename__ = 'post'

    post_id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("user.user_id"), nullable=False)
    post_title = Column(Text, nullable=False)
    post_content = Column(Text)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    # is_report = Column(Boolean, default=False)

    # 관계설정
    user = relationship("User", back_populates="posts")
    comments = relationship("PostComment", back_populates="post")
    images = relationship("PostImage", back_populates="post")
    view_count = relationship("PostViewCount", back_populates="post", uselist=False)
    like_count = relationship("PostLikeCount", back_populates="post", uselist=False)
    comment_count = relationship("PostCommentCount", back_populates="post", uselist=False)
    likes = relationship("PostLike", back_populates="post")

    # post_hobby_tag를 Post 모델에서 두 번 참조해서 중복 경고 해소
    post_tags = relationship(
        "PostHobbyTag",
        back_populates="post",
        overlaps="post_hobby_tags"
    )

    post_hobby_tags = relationship(
        "PostHobbyTag",
        back_populates="post",
        cascade="all, delete-orphan",
        overlaps="post_tags"
    )

    @property
    def comment_count_value(self):
        # 댓글 개수 반환
        return self.comment_count.comment_count if self.comment_count else 0
    
    @classmethod
    def get_related_models(cls):
        from . import (
            user, post_comment, post_like, post_view_count,
            post_like_count, post_hobby_tag, post_comment_count
        )
        return (
            user, post_comment, post_like, post_view_count,
            post_like_count, post_hobby_tag, post_comment_count
        )
