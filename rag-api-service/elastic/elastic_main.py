from app.config import settings
from elasticsearch import Elasticsearch

vec_uri = settings.VEC_URI
collection_name = settings.COLLECTION_NAME
VEC_DIM = settings.VEC_DIM

es = Elasticsearch(vec_uri)

def create_index() -> None:
    mapping = {
        "mappings": {
            "properties": {
                "id": {"type": "long"},
                "source": {"type": "long"},
                "text": {"type": "text"},
                "tg_link": {"type": "keyword"},
                "embeddings": {
                    "type": "dense_vector",
                    "dims": VEC_DIM,
                    "index": True,
                    "similarity": "cosine"
                }
            }
        }
    }
    if not es.indices.exists(index=collection_name):
        es.indices.create(index=collection_name, body=mapping)

create_index()


