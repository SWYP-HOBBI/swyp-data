# # elastic/es_client.py
# from elasticsearch import Elasticsearch
# from typing import List, Optional, Any,Dict
# from datetime import datetime
# import logging

# # 로깅 설정
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # 엘라스틱서치 클라이언트 초기화
# # 실제 환경에서는 설정 파일 등에서 주소를 가져오는 것이 좋습니다.
# ES_HOST = "http://127.0.0.1:9200" # 로컬 테스트용
# # ES_HOST = "http://110.165.16.69:8000" # 실제 서버 테스트

# ES_INDEX_POSTS = "post_index" # 실제 인덱스 이름 확인

# # https는 ca 인증서가 필요함 그래서 ca 인증서 path 추가
# # CA_CERT_PATH = "/Users/ijaewon/elasticsearch-9.0.0/config/certs/http_ca.crt"
# # http는 Elasticsearch로의 모든 통신이 암호화되지 않아서 https로 진행


# # try:
# #     es = Elasticsearch(
# #         ES_HOST,
# #         request_timeout=60
# #         #### 아래는 https 연결 시 필요한 것들
# #         # verify_certs=True,  # SSL 인증서 검증 활성화
# #         # ca_certs=CA_CERT_PATH, # CA 인증서 파일 경로 지정
# #         # ssl_assert_hostname=False # 호스트 이름 검증 비활성화
# #     )
# #     es.info() # 연결 테스트
# #     logger.info(f"Elasticsearch connection successful to {ES_HOST} with CA certificate.")
# # except Exception as e:
# #     logger.error(f"Elasticsearch connection failed to {ES_HOST} with CA certificate: {e}")
# #     # 연결 실패 시 예외 처리 또는 폴백 로직 추가 필요
# #     # 예시로 더미 클라이언트 사용
# #     class DummyElasticsearch:
# #         def search(self, index: str, body: dict) -> dict:
# #             logger.warning("Using dummy Elasticsearch client. ES connection failed.")
# #             return {"hits": {"hits": []}}
# #         def info(self):
# #             pass
# #         def connected(self): # 연결 상태 확인 메서드 추가 (가짜)
# #             return False

# #     es = DummyElasticsearch()
# # 실제 Elasticsearch 클라이언트만 사용하도록 설정
# es = Elasticsearch(ES_HOST, request_timeout=60)
# if not es.ping():
#     logger.error(f"Could not ping Elasticsearch at {ES_HOST}")
# else:
#     logger.info(f"Connected to Elasticsearch at {ES_HOST}")

# # 입력 파라미터
# def search_post_ids_from_es(
#     keyword: Optional[str] = None,
#     mbti: Optional[List[str]] = None,
#     hobby_tags: Optional[List[int]] = None,
#     cursor_created_at: Optional[datetime] = None,
#     cursor_id: Optional[int] = None,
#     limit: int = 15,
# ) -> List[int]:
#     # 반환값: 검색된 post_id 리스트 (List[int])

#     must_clauses: List[Dict[str, Any]] = []

#     if keyword:
#         must_clauses.append({
#             "multi_match": {
#                 "query": keyword,
#                 "fields": ["post_title", "post_content", "user_nickname", "comments.comment_content"],
#                 "type": "best_fields",
#                 "operator": "or"
#             }
#         })
#     # keyword: multi_match 쿼리로 여러 필드(post_title, post_content, user_nickname, comments.comment_content)를 한 번에 검색    

#     if mbti:
#         mbti_filters = [{"wildcard": {"user_mbti": f"*{t.upper()}*"}} for t in mbti]
#         must_clauses.append({"bool": {"must": mbti_filters}})
#     # mbti: 각각의 MBTI 문자를 와일드카드(*I*, *N* 등)로 검색 → bool.must 안에 묶어서 모두 만족

#     if hobby_tags:
#         must_clauses.append({"terms": {"hobby_tag_ids": hobby_tags}})
#     # hobby_tags: 정수 배열 필드(hobby_tag_ids)가 주어진 리스트 안에 포함된 문서만 매칭

#     query_body: Dict[str, Any] = {
#         "query": {"bool": {"must": must_clauses}} if must_clauses else {"match_all": {}},
#         "_source": ["post_id"],
#         "size": limit + 1,
#         "sort": [{"created_at": {"order": "desc"}}, {"post_id": {"order": "desc"}}]
#     }
#     # query: must_clauses가 있으면 bool.must로 묶고, 없으면 match_all
#     # _source: 반환 필드를 post_id로 최소화 → 네트워크·메모리 절약
#     # size: limit + 1 로 가져와서 “다음 페이지 존재 여부”를 파악 후 슬라이스
#     # sort: created_at(desc), post_id(desc) 순으로 정렬 → 커서 기반 페이징 시 일관성 확보
#     # search_after: 이전 페이지 마지막 문서의 created_at과 post_id를 배열로 넘겨, 다음 페이지 문서부터 시작


#     if cursor_created_at is not None and cursor_id is not None:
#         query_body["search_after"] = [cursor_created_at.isoformat(), cursor_id]
#         logger.info(f"Using search_after: {query_body['search_after']}")

#     try:
#         logger.info(f"ES query: {query_body}")
#         res = es.search(index=ES_INDEX_POSTS, body=query_body)
#         hits = res.get("hits", {}).get("hits", [])
#         post_ids = [hit["_source"]["post_id"] for hit in hits if "_source" in hit]
#         logger.info(f"Found {len(post_ids)} IDs in ES")
#         return post_ids
#     except Exception as e:
#         logger.error(f"Error during ES search: {e}")
#         return []
#     # es.search: 주어진 인덱스(post_index)에 HTTP GET _search 요청
#     # res["hits"]["hits"]: 실제 매칭된 도큐먼트 리스트
#     # _source 확인 후 post_id만 추출
#     # 예외 처리: ES 접속 오류, 쿼리 오류 등 발생 시 빈 리스트 반환


# elastic/es_client.py

from elasticsearch import Elasticsearch
from typing import List, Optional, Any, Dict
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ES_HOST = "http://127.0.0.1:9200"
ES_INDEX_POSTS = "post_index"

es = Elasticsearch(ES_HOST, request_timeout=60)
if not es.ping():
    logger.error(f"Could not ping Elasticsearch at {ES_HOST}")
else:
    logger.info(f"Connected to Elasticsearch at {ES_HOST}")

def search_post_ids_from_es(
    keyword: Optional[str] = None,
    fields: Optional[List[str]] = None,
    mbti: Optional[List[str]] = None,
    hobby_tags: Optional[List[int]] = None,
    cursor_created_at: Optional[datetime] = None,
    cursor_id: Optional[int] = None,
    limit: int = 15,
) -> List[int]:
    """
    ES에서 post_id 리스트를 가져옵니다.
    - 개발 중: 새로 저장된 문서가 바로 검색되도록 refresh를 강제합니다.
    """

    # ── 개발·디버깅용: 최신 데이터가 검색에 반영되도록 인덱스 강제 리프레시
    try:
        es.indices.refresh(index=ES_INDEX_POSTS)
    except Exception as e:
        logger.warning(f"ES refresh failed: {e}")

    """
    ES에서 post_id 리스트를 가져옵니다.
    - keyword: 검색어
    - fields: multi_match 적용할 필드 리스트 (기본: ['post_title','post_content'])
    - mbti, hobby_tags: 필터용
    - cursor_created_at, cursor_id: 페이징용 search_after
    - limit: 가져올 개수 (size = limit+1)
    """
    # 기본 검색 필드
    if fields is None:
        fields = ["post_title", "post_content"]

    must_clauses: List[Dict[str, Any]] = []

    # 1) 텍스트 검색
    if keyword:
        must_clauses.append({
            "multi_match": {
                "query": keyword,
                "fields": fields,
                "type": "best_fields",
                "operator": "or",
                "minimum_should_match": "75%"  # ← 더 유연하게
            }
        })

    # 2) MBTI 필터
    if mbti:
        mbti_filters = [{"wildcard": {"user_mbti": f"*{t.upper()}*"}} for t in mbti]
        must_clauses.append({"bool": {"must": mbti_filters}})

    # 3) Hobby Tag 필터
    if hobby_tags:
        must_clauses.append({"terms": {"hobby_tag_ids": hobby_tags}})

    # 4) 베이스 쿼리
    query_body: Dict[str, Any] = {
        "query": {"bool": {"must": must_clauses}} if must_clauses else {"match_all": {}},
        "_source": ["post_id"],
        "size": limit + 1,
        "sort": [
            {"created_at": {"order": "desc"}},
            {"post_id": {"order": "desc"}}
        ]
    }

    # 5) 커서 페이징(search_after)
    if cursor_created_at is not None and cursor_id is not None:
        query_body["search_after"] = [cursor_created_at.isoformat(), cursor_id]
        logger.info(f"Using search_after: {query_body['search_after']}")

    try:
        logger.info(f"ES query: {query_body}")
        res = es.search(index=ES_INDEX_POSTS, body=query_body)
        hits = res.get("hits", {}).get("hits", [])
        post_ids = [hit["_source"]["post_id"] for hit in hits if "_source" in hit]
        logger.info(f"Found {len(post_ids)} IDs in ES")
        return post_ids
    except Exception as e:
        logger.error(f"Error during ES search: {e}")
        return []