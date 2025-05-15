import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import Column, BigInteger, String, ForeignKey, VARCHAR
from sqlalchemy.orm import relationship
from database import Base

class PostImage(Base):
    __tablename__ = "post_image"

    image_id = Column(BigInteger, primary_key=True, index=True)
    post_id = Column(BigInteger, ForeignKey("post.post_id"), nullable=False)
    image_file_name = Column(VARCHAR, nullable=False)
    image_url = Column(VARCHAR, nullable=False)

    post = relationship("Post", back_populates="images")
