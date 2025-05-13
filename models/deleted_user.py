import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import Column, BigInteger, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class DeletedUser(Base):
    __tablename__ = "deleted_user"

    user_id = Column(BigInteger, ForeignKey("user.user_id"), primary_key=True)
    delete_message = Column(Text)

    user = relationship("User", back_populates="deleted_user")
