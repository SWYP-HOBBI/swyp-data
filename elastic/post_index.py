# elastic/post_index.py
from elasticsearch import Elasticsearch, NotFoundError
from typing import List, Dict, Any
import logging
from sqlalchemy.orm import Session
from database import SessionLocal  # DB 연결 세션
from models import post as post_model
from models.user import User  # 유저 닉네임 추출용

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

ES_HOST = "http://127.0.0.1:9200"
ES_INDEX = "post_index"

es = Elasticsearch(ES_HOST, request_timeout=60)
if not es.ping():
    logger.error(f"Could not ping Elasticsearch at {ES_HOST}")
else:
    logger.info(f"Connected to Elasticsearch at {ES_HOST}")

POST_INDEX_MAPPING: Dict[str, Any] = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "analysis": {
            "tokenizer": {
                "edge_ngram_tokenizer": {
                    "type": "edge_ngram",
                    "min_gram": 1,
                    "max_gram": 10,
                    "token_chars": ["letter", "digit"]
                }
            },
            "analyzer": {
                "edge_ngram_analyzer": {
                    "type": "custom",
                    "tokenizer": "edge_ngram_tokenizer"
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "post_id": {"type": "integer"},
            "post_title": {"type": "text", "analyzer": "edge_ngram_analyzer"},
            "post_content": {"type": "text", "analyzer": "edge_ngram_analyzer"},
            "user_nickname": {"type": "keyword"},
            "created_at": {"type": "date"}
        }
    }
}

def create_index(force: bool = False) -> None:
    if force and es.indices.exists(index=ES_INDEX):
        es.indices.delete(index=ES_INDEX)
        logger.info(f"Deleted existing index '{ES_INDEX}'")

    if not es.indices.exists(index=ES_INDEX):
        es.indices.create(index=ES_INDEX, body=POST_INDEX_MAPPING)
        logger.info(f"Created index '{ES_INDEX}' with mapping")
    else:
        logger.info(f"Index '{ES_INDEX}' already exists")

from elasticsearch.helpers import bulk

def bulk_index_posts(docs: List[Dict[str, Any]], chunk_size: int = 500) -> None:
    actions = [
        {"_index": ES_INDEX, "_id": doc["post_id"], "_source": doc}
        for doc in docs
    ]
    success, _ = bulk(client=es, actions=actions, chunk_size=chunk_size)
    logger.info(f"Bulk indexed {success} posts")

def reindex_all_posts_from_db():
    from models import get_related_models
    get_related_models()

    create_index(force=True)
    db: Session = SessionLocal()
    posts = db.query(post_model.Post).join(User).all()

    docs = []
    for post in posts:
        docs.append({
            "post_id": post.post_id,
            "post_title": post.post_title,
            "post_content": post.post_content,
            "user_nickname": post.user.nickname,
            "created_at": post.created_at.isoformat()
        })

    bulk_index_posts(docs)
    db.close()
    return len(docs)

if __name__ == "__main__":
    count = reindex_all_posts_from_db()
    logger.info(f"Reindexed {count} posts")
