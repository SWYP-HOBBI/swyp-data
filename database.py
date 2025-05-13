# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# db 주소
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:dbdbdbdb@localhost:3306/swyp"
# 실 사용 db
# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://hobbi:hobbi1234!@db-33uu5c-kr.vpc-pub-cdb.ntruss.com:3306/hobbi"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
