import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import Column, BigInteger, String,VARCHAR
from sqlalchemy.orm import relationship
from database import Base

class HobbyTag(Base):
    __tablename__ = "hobby_tag"

    hobby_tag_id = Column(BigInteger, primary_key=True, index=True)
    hobby_tag_name = Column(VARCHAR(255), nullable=False)
    hobby_type = Column(VARCHAR(30), nullable=False)

    user_hobby_tags = relationship("UserHobbyTag", back_populates="hobby_tag")
    post_hobby_tags = relationship("PostHobbyTag", back_populates="hobby_tag")

