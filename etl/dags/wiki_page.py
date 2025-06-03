from airflow.decorators import dag
from airflow.utils.dates import days_ago
from pendulum import datetime
import requests
from airflow.operators.python import PythonOperator
from services.base_service import html_splitter, insert_data, delete_raws_by_source
from services.base_service import has_milvus_collection, load_milvus_collection
import base64
import os
import json


BI_ENCODER_URL = os.getenv("AIRFLOW_VAR_ENCODER_URL")
WIKI_URI = os.getenv("AIRFLOW_VAR_WIKI_URI")
WIKI_USER = os.getenv("AIRFLOW_VAR_WIKI_USER")
WIKI_PASS = os.getenv("AIRFLOW_VAR_WIKI_PASS")
PAGE_ID = os.getenv("AIRFLOW_VAR_PAGE_ID")
CHUNK_SIZE = int(os.getenv("AIRFLOW_VAR_CHUNK_SIZE"))
OVERLAP = int(os.getenv("AIRFLOW_VAR_OVERLAP"))


def delete_page_by_id():

    if has_milvus_collection():
        load_milvus_collection()
        delete_raws_by_source(int(PAGE_ID))


def get_wiki_page_by_id(ti):

    url = WIKI_URI + PAGE_ID + "/?expand=body.storage"
    auth_header = "Basic " + base64.b64encode(f"{WIKI_USER}:{WIKI_PASS}".encode()).decode()

    headers = {
        "Authorization": auth_header
    }

    response = requests.get(url, headers=headers, verify="./dags/cert.pem")

    ti.xcom_push("wiki_page", response.json()["body"]["storage"]["value"])


def split_wiki_page(ti):

    html_wiki_page = ti.xcom_pull(key="wiki_page", task_ids="get_wiki_page")

    chunks = html_splitter(html_wiki_page, 
                           [
                                ("h1", "Header 1"),
                                ("h2", "Header 2"),
                                ("h3", "Header 3"),
                                ("h4", "Header 4"),
                                ("h5", "Header 5"),
                                ("h6", "Header 6")
                            ], 
                            CHUNK_SIZE, OVERLAP)
    
    source_chunks = []

    for chunk in chunks:
        source_chunks.append(' '.join(chunk.metadata.values()) + ". " + chunk.page_content)

    ti.xcom_push("source_chunks", source_chunks)


def vectorize_chunks(ti):
    
    chunks = ti.xcom_pull(key="source_chunks", task_ids="split_page")

    data_rows = []

    for chunk in chunks:

        headers = {'Content-type': 'application/json'}
        request = {'chunk': chunk}
        
        response = requests.get(url=BI_ENCODER_URL,
                                data=json.dumps(request), 
                                headers=headers)
        vec = response.json()

        data_rows.append({"source": int(PAGE_ID), 
                          "embeddings": vec["vector"],
                          "text": chunk, 
                          "tg_link": ""})
    
    insert_data(data_rows)



@dag(
    start_date=days_ago(1),
    schedule_interval='0 0 * * *',
    catchup=False,
    render_template_as_native_obj=True
)
def load_wiki():

    delete_page = PythonOperator(
        task_id="delete_page", python_callable=delete_page_by_id
    )

    get_wiki_page = PythonOperator(
        task_id="get_wiki_page", python_callable=get_wiki_page_by_id
    )


    split_page = PythonOperator(
        task_id="split_page", python_callable=split_wiki_page
    )


    vectorize = PythonOperator(
        task_id="vectorize_chunks", python_callable=vectorize_chunks
    )
    
   
    delete_page >> get_wiki_page >> split_page >> vectorize

load_wiki()
