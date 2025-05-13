import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import Column, BigInteger, String, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from database import Base

class PostViewCount(Base):
    __tablename__ = 'PostViewCount'
    
    post_id = Column(BigInteger, ForeignKey("post.post_id"), primary_key=True, nullable=False)
    view_count = Column(BigInteger, nullable=False, default=0)

    # 관계설정
    post = relationship("Post", back_populates="view_count")