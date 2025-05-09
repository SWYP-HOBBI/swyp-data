from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import search,post
import models
from database import Base, engine

# 모델 테이블 생성 전에 관계 설정
models.get_related_models()

# 테이블 생성
Base.metadata.create_all(bind=engine)

# FastAPI 앱 설정
app = FastAPI()

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],                      # Next.js 개발 서버 도메인
    allow_credentials=True,                   # 브라우저에서 쿠키/인증 헤더 등의 포함 여부를 허용할지 설정  
    allow_methods=["*"],                      # 어떤 HTTP 메서드를 허용할지 지정 (GET, POST 등)
    allow_headers=["*"],                      # 어떤 헤더들을 허용할지 지정 (Authorization, Content-Type 등)
)

# 라우터 등록
app.include_router(search.router)
app.include_router(post.router)


