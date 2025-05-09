import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import Column, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class PostViewCount(Base):
    __tablename__ = "post_view_count"

    post_id = Column(BigInteger, ForeignKey("post.post_id"), primary_key=True)
    view_count = Column(BigInteger, default=0)

    post = relationship("Post", back_populates="view_count")