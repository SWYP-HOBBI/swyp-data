import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import Column, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class PostCommentCount(Base):
    __tablename__ = "post_comment_count"

    post_id = Column(BigInteger, ForeignKey("post.post_id"), primary_key=True)
    comment_count = Column(BigInteger)

    # Post와 1:1 관계
    post = relationship("Post", back_populates="comment_count")
