import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import Column, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class PostLikeCount(Base):
    __tablename__ = "post_like_count"

    post_id = Column(BigInteger, ForeignKey("post.post_id"), primary_key=True)
    like_count = Column(BigInteger)
    version = Column(BigInteger, nullable=False)

    post = relationship("Post", back_populates="like_count")
