from airflow.decorators import dag, task
from airflow.providers.amazon.aws.sensors.s3_key import S3KeySensor
from airflow.utils.dates import days_ago
from datetime import timedelta, datetime, timezone
import os
import boto3
import requests
from docx import Document as DocxDocument
from services.base_service import (
    clean_text, 
    filter_chunks, 
    deduplicate_chunks, 
    is_heading, 
    split_by_sentences
)
from elasticsearch import Elasticsearch

S3_BUCKET = os.getenv("S3_BUCKET")
S3_PREFIX = os.getenv("S3_PREFIX")
LOCAL_DOWNLOAD_DIR = os.getenv("LOCAL_DOWNLOAD_DIR", "/tmp/documents")
ENCODER_URL = os.getenv("ENCODER_URL")
ELASTICSEARCH_URI = os.getenv("ELASTICSEARCH_URI")
INDEX_NAME = os.getenv("INDEX_NAME")
VEC_DIM = int(os.getenv("VEC_DIM", 768))

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

@dag(
    dag_id='s3_pipeline_dag_decorator',
    default_args=default_args,
    description='ETL pipeline: мониторинг S3, загрузка, парсинг, векторизация и индексация',
    schedule_interval=timedelta(minutes=10),
    start_date=days_ago(1),
    catchup=False,
    max_active_runs=1
)
def s3_pipeline_dag():
    s3_sensor = S3KeySensor(
        task_id='s3_file_sensor',
        bucket_key=f"{S3_PREFIX}*",
        wildcard_match=True,
        bucket_name=S3_BUCKET,
        aws_conn_id='aws_default',
        poke_interval=60,
        timeout=60 * 5,
        mode='poke'
    )


    @task
    def list_new_files() -> list[str]:
        """
        Ищем новые или обновленные файлы в S3 (например, за последние 10 минут).
        """
        s3 = boto3.client('s3')
        response = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=S3_PREFIX)
        new_files = []

        if 'Contents' in response:
            for obj in response['Contents']:
                key = obj['Key']
                last_modified = obj['LastModified']
                if last_modified >= datetime.now(timezone.utc) - timedelta(minutes=10):
                    new_files.append(key)

        return new_files


    @task
    def download_file(s3_key: str) -> str:
        s3 = boto3.client('s3')
        os.makedirs(LOCAL_DOWNLOAD_DIR, exist_ok=True)
        local_path = os.path.join(LOCAL_DOWNLOAD_DIR, os.path.basename(s3_key))
        s3.download_file(S3_BUCKET, s3_key, local_path)
        return local_path


    @task
    def parse_and_chunk_docx(local_path: str) -> list[str]:
        doc = DocxDocument(local_path)
        sections = []
        current_section = ""
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue
            if is_heading(para):
                if current_section:
                    sections.append(current_section.strip())
                    current_section = ""
                current_section += text + "\n"
            else:
                current_section += text + " "
        all_chunks = []
        for section in sections:
            raw_chunks = split_by_sentences(section)
            cleaned_chunks = [clean_text(c) for c in raw_chunks]
            filtered_chunks = filter_chunks(cleaned_chunks)
            all_chunks.extend(filtered_chunks)
        all_chunks = deduplicate_chunks(all_chunks)
        return all_chunks


    @task
    def encode_chunks(chunks: list[str]) -> list[list[float]]:
        vectors = []
        for chunk in chunks:
            payload = {"chunk": chunk}
            response = requests.post(ENCODER_URL, json=payload)
            response.raise_for_status()
            vector = response.json()["vector"]
            vectors.append(vector)
        return vectors


    @task
    def index_chunks(local_path: str, chunks: list[str], vectors: list[list[float]]):
        es = Elasticsearch(ELASTICSEARCH_URI)
        doc_id = hash(local_path)
        for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
            doc = {
                "id": i,
                "source": doc_id,
                "text": chunk,
                "tg_link": "",
                "embeddings": vector
            }
            es.index(index=INDEX_NAME, body=doc)

    new_files = list_new_files()
    downloaded_files = download_file.expand(s3_key=new_files)
    chunks = parse_and_chunk_docx.expand(local_path=downloaded_files)
    vectors = encode_chunks.expand(chunks=chunks)
    index_chunks.expand(local_path=downloaded_files, chunks=chunks, vectors=vectors)

    s3_sensor >> new_files

dag_instance = s3_pipeline_dag()
