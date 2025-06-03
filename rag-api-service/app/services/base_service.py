from datetime import datetime
from typing import List
from config import settings
import re
import requests
import json
from elastic.elastic_main import es


def vectorize_question(question: str) -> List:
    headers = {'Content-type': 'application/json'}
    request = {'chunk': question}
        
    response = requests.post(url=settings.ENCODER_URL, data=json.dumps(request), headers=headers)

    return response.json()["vector"]


def vector_to_text(question: str,
                   question_vector: List[float],
                   limit: int,
                   score_threshold: float = 0.75) -> str:
    """
    Выполняет гибридный поиск в Elasticsearch и формирует текстовый ответ.
    """
    answer = ""

    hybrid_query = {
        "bool": {
            "should": [
                {
                    "knn": {
                        "field": "embeddings",
                        "query_vector": question_vector,
                        "k": limit,
                        "num_candidates": 100
                    }
                },
                {
                    "match": {
                        "text": {
                            "query": question,
                            "boost": 2.0
                        }
                    }
                }
            ]
        }
    }

    response = es.search(
        index=settings.COLLECTION_NAME,
        body={
            "size": limit,
            "query": hybrid_query
        }
    )

    hits = response["hits"]["hits"]
    for index, hit in enumerate(hits):
        score = hit["_score"]

        if score >= score_threshold:
            source = hit["_source"]
            text = source.get("text", "")
            answer += f"\n Текстовый блок №{index}: {text}"

    return answer


def load_document_text(url: str) -> str:
    match_ = re.search('/document/d/([a-zA-Z0-9-_]+)', url)

    if match_ is None:
        raise ValueError('Invalid Google Docs URL')
    
    doc_id = match_.group(1)
    response = requests.get(f'https://docs.google.com/document/d/{doc_id}/export?format=txt')
    response.raise_for_status()
    text = response.text

    return text


def get_current_date_time() -> datetime:
    return datetime.now()