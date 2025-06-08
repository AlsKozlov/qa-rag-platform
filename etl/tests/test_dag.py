from airflow.models import DagBag

def test_s3_chunker_dag_loaded():
    dagbag = DagBag(dag_folder="etl/dags")
    assert "s3_pipeline_dag" in dagbag.dags

def test_s3_chunker_dag_tasks():
    dagbag = DagBag(dag_folder="etl/dags")
    dag = dagbag.get_dag("s3_pipeline_dag")
    task_ids = list(dag.task_ids)
    expected = [
        's3_file_sensor',
        'download_file',
        'parse_and_chunk',
        'encode_chunks',
        'index_chunks'
    ]
    for task in expected:
        assert task in task_ids
