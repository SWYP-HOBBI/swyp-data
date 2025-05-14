import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import Column, BigInteger, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Notification(Base):
    __tablename__ = "notification"

    notification_id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user.user_id"), nullable=False)
    notification_type = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, nullable=False)
    created_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="notifications")
