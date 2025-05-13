import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import Column, BigInteger, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from database import Base

class PostComment(Base):
    __tablename__ = "post_comment"

    comment_id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("user.user_id"), nullable=False)
    post_id = Column(BigInteger, ForeignKey("post.post_id"), nullable=False)
    parent_comment_id = Column(BigInteger, ForeignKey("post_comment.comment_id"))
    comment_content = Column(Text)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    post = relationship("Post", back_populates="comments")
    user = relationship("User", back_populates="comments")