import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import Column, BigInteger, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class PostLike(Base):
    __tablename__ = "post_like"

    post_like_id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user.user_id"), nullable=False)
    post_id = Column(BigInteger, ForeignKey("post.post_id"), nullable=False)
    likeYn = Column(BigInteger)
    like_created_at = Column(DateTime)

    post = relationship("Post", back_populates="likes")
