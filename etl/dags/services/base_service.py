from langchain_text_splitters import HTMLHeaderTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from pymilvus import MilvusClient
from typing import List


VEC_URI = os.getenv("AIRFLOW_VAR_VEC_URI")
COLLECTION_NAME = os.getenv("AIRFLOW_VAR_COLLECTION_NAME")

MILVUS_CLIENT = MilvusClient(uri=VEC_URI)


def has_milvus_collection() -> bool:

    return MILVUS_CLIENT.has_collection(collection_name=COLLECTION_NAME)


def insert_data(data: list):

    MILVUS_CLIENT.insert(collection_name="", data=data)


def delete_raws_by_source(source):

    MILVUS_CLIENT.delete(
        collection_name=COLLECTION_NAME,
        filter= f"source == {source}"
    )


def load_milvus_collection():
    MILVUS_CLIENT.load_collection(collection_name=COLLECTION_NAME)


def html_splitter(html_string, 
                  headers_to_split_on, 
                  chunk_size, 
                  chunk_overlap) -> List:

  html_splitter = HTMLHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

  html_header_splits = html_splitter.split_text(html_string)

  text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, 
                                                 chunk_overlap=chunk_overlap, 
                                                 separators=["\n\n", "\n", "</strong>"])

  splits = text_splitter.split_documents(html_header_splits)

  return splits