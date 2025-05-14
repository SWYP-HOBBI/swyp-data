# routers/admin.py
from fastapi import APIRouter
from elastic.post_index import reindex_all_posts_from_db

router = APIRouter(prefix="/fastapi/v1/admin", tags=["Admin"])

@router.post("/reindex")
def reindex_all():
    count = reindex_all_posts_from_db()
    return {"status": "ok", "indexed": count}



### postman에서 
# 주기적으로 POST http://localhost:8000/fastapi/v1/admin/reindex    실행
# {
#   "status": "ok",
#   "indexed": 30  // 색인된 게시글 수
# }


