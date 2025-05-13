import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import Column, BigInteger, String, Boolean, Text, Integer, DateTime, CHAR
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "user"

    user_id = Column(BigInteger, primary_key=True, index=True)
    email = Column(String(255), nullable=False)
    username = Column(String(30), nullable=False)
    password = Column(String(255), nullable=False)
    nickname = Column(String(30), nullable=False)
    birth_year = Column(Integer, nullable=False)
    birth_month = Column(Integer, nullable=False)
    birth_day = Column(Integer, nullable=False)
    gender = Column(CHAR(30), nullable=False)
    mbti = Column(String(12))
    user_image_url = Column(Text, nullable=False)
    role = Column(Text, nullable=False)
    is_tag_exist = Column(Boolean, nullable=False)
    is_blocked = Column(Boolean, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)


    posts = relationship("Post", back_populates="user")
    hobby_tags = relationship("UserHobbyTag", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    deleted_user = relationship("DeletedUser", back_populates="user", uselist=False)
    comments = relationship("PostComment",back_populates="user")
