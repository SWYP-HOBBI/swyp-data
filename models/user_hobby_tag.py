import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import Column, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class UserHobbyTag(Base):
    __tablename__ = "user_hobby_tag"

    user_hobby_tag_id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user.user_id"), nullable=False)
    hobby_tag_id = Column(BigInteger, ForeignKey("hobby_tag.hobby_tag_id"), nullable=False)

    user = relationship("User", back_populates="hobby_tags")
    hobby_tag = relationship("HobbyTag", back_populates="user_hobby_tags")
