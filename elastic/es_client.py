from elasticsearch import Elasticsearch
from typing import List

es = Elasticsearch("http://localhost:9200")

def search_posts_by_keyword(keyword: str) -> List[int]:
    body = {
        "query": {
            "multi_match": {
                "query": keyword,
                "fields": ["post_title", "post_content", "user_nickname", "comments.comment_content"]
            }
        }
    }

    res = es.search(index="posts_index", body=body)
    hits = res.get("hits", {}).get("hits", [])
    
    post_ids = [hit["_source"]["post_id"] for hit in hits]
    return post_ids

