# from airflow.decorators import dag, task
# from pendulum import datetime
# import requests
# from services.base_service import insert_data, delete_raws_by_source
# from airflow.providers.apache.kafka.operators.consume import ConsumeFromTopicOperator
# from airflow.operators.python import PythonOperator, BranchPythonOperator

# from langchain.text_splitter import CharacterTextSplitter
# from langchain.docstore.document import Document

# import json

# KAFKA_TOPIC = "llm.second_memory.wiki"

# def consume_kafka_messages(message, ti):

#     message_content = json.loads(message.value())

#     ti.xcom_push("page_id", message_content["page"]["id"])
#     ti.xcom_push("event", message_content["event"])


# def choose_process_by_event(ti):
    
#     event = ti.xcom_pull(key="event", task_ids="consume_message")

#     if event == "page_created":
#         return "page_created"
#     elif event == "page_removed":
#         return "delete_page"
#     elif event == "page_updated":
#         return "get_wiki_page"
#     else:
#         return "error_message"


# def delete_page_by_source(ti):

#     page_id = ti.xcom_pull(key="page_id", task_ids="consume_message")

#     delete_raws_by_source(page_id)


# def get_wiki_page_by_id(ti):

#     page_id = ti.xcom_pull(key="page_id", task_ids="consume_message")


# def split_wiki_page(ti):

#     text = ti.xcom_pull(key="page_id", task_ids="consume_message")

#     source_chunks = []
#     splitter = CharacterTextSplitter(separator="\r\n", chunk_size=200, chunk_overlap=0)

#     for chunk in splitter.split_text(text):
#         source_chunks.append(Document(page_content=chunk, metadata={}))

#     ti.xcom_push("source_chunks", source_chunks)


# def vectorize_chunks(ti):
    
#     chunks = ti.xcom_pull(key="source_chunks", task_ids="split_page")
#     source = ti.xcom_pull(key="page_id", task_ids="consume_message")

#     data = []

#     for chunk in chunks:
#         headers = {'Content-type': 'application/json'}
#         request = {'chunk': chunk}
        
#         response = requests(method='GET', url=settings.ENCODER_URI,
#                                 data=json.dumps(request), headers=headers)
#         vec = response.text

#         data.append(source,
#                     vec,
#                     chunk,
#                     "")
    
#     insert_data(data)


# @dag(
#     start_date=datetime(2024, 6, 9),
#     schedule=None,
#     catchup=False,
#     render_template_as_native_obj=True
# )
# def load_wiki_pages():

#     consume_message = ConsumeFromTopicOperator(
#         task_id="consume_message",
#         kafka_config_id="kafka_con",
#         topics=[KAFKA_TOPIC],
#         apply_function=consume_kafka_messages,
#         poll_timeout=20,
#         max_messages=20,
#         max_batch_size=20,
#     )

#     choose_best_model = BranchPythonOperator(
#         task_id='choose_process',
#         python_callable=choose_process_by_event
#     )


#     get_wiki_page = PythonOperator(
#         task_id="get_wiki_page", python_callable=get_wiki_page_by_id
#     )


#     split_page = PythonOperator(
#         task_id="split_page", python_callable=split_wiki_page
#     )

#     vectorize = PythonOperator(
#         task_id="vectorize_chunks", python_callable=vectorize_chunks
#     )
    
#     delete_page = PythonOperator(
#         task_id="delete_page", python_callable=delete_page_by_source
#     )

#     consume_message >> choose_best_model >> [get_wiki_page >> split_page >> vectorize, 
#                                              delete_page, 
#                                              delete_page >> get_wiki_page >> split_page >> vectorize]

# load_wiki_pages()
