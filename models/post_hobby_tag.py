import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import Column, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class PostHobbyTag(Base):
    __tablename__ = "post_hobby_tag"

    post_hobby_tag_id = Column(BigInteger, primary_key=True, index=True)
    post_id = Column(BigInteger, ForeignKey("post.post_id"), nullable=False)
    hobby_tag_id = Column(BigInteger, ForeignKey("hobby_tag.hobby_tag_id"), nullable=False)

    post = relationship("Post", back_populates="post_hobby_tags")
    hobby_tag = relationship("HobbyTag", back_populates="post_hobby_tags")
    
