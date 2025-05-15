import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import Column, BigInteger, String, Boolean, Text, Integer, DateTime, CHAR, VARCHAR
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "user"

    user_id = Column("user_id", BigInteger, primary_key=True, index=True)
    email = Column("email", String(255), nullable=False)
    username = Column("username", String(30), nullable=False)
    password = Column("password",String(255), nullable=False)
    nickname = Column("nickname",String(30), nullable=False)
    birth_year = Column("birth_year",Integer, nullable=False)
    birth_month = Column("birth_month",Integer, nullable=False)
    birth_day = Column("birth_day",Integer, nullable=False)
    gender = Column("gender",CHAR(30), nullable=False)
    mbti = Column("mbti",String(12))
    user_image_url = Column("user_image_url", Text, nullable=False)
    role = Column("role",Text, nullable=False)
    is_tag_exist = Column("is_tag_exist",Boolean, nullable=False)
    is_blocked = Column("is_blocked",Boolean, nullable=False)
    created_at = Column("created_at",DateTime, nullable=False)
    updated_at = Column("updated_at",DateTime, nullable=False)
    # provider      = Column("provider",     String(50),  nullable=True)
    # provider_id   = Column("provider_id", BigInteger, nullable=True)


    posts         = relationship("Post", back_populates="user")
    hobby_tags    = relationship("UserHobbyTag", back_populates="user")
    deleted_user  = relationship("DeletedUser", back_populates="user", uselist=False)
    comments      = relationship("PostComment", back_populates="user")

