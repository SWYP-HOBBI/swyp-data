from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas.search import SearchRequest
from services.search_service import search_posts

router = APIRouter(prefix="/fastapi/v1/search", tags=["Search"])

@router.post("/")
def search(req: SearchRequest, db: Session = Depends(get_db)):
    return search_posts(db, req)
