import os
import sys

# 현재 경로 기준으로 PYTHONPATH 세팅
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import get_related_models
from database import Base, engine

# 모델 모듈 전체 import (순환 참조 대비용)
get_related_models()

# 테이블 생성
print("creat all table")
Base.metadata.create_all(bind=engine)
print("Done.")
