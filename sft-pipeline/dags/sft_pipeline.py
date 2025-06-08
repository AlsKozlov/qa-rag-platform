import os
from airflow.decorators import dag, task
from airflow.providers.amazon.aws.sensors.s3_key import S3KeySensor
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
from services.run_pipeline_service import run_pipeline
from dotenv import load_dotenv

load_dotenv()

S3_BUCKET = os.getenv("S3_BUCKET")
S3_PREFIX = os.getenv("S3_PREFIX")
S3_KEY = os.getenv("S3_KEY")
LOCAL_DATA_PATH = os.getenv("LOCAL_DATA_PATH", "/data/qa_dataset.csv")
MODEL_SAVE_PATH = os.getenv("MODEL_SAVE_PATH", "./model/")
MODEL_NAME = os.getenv("MODEL_NAME", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
METRICS_THRESHOLD = float(os.getenv("METRICS_THRESHOLD"))
VALIDATION_DATA_PATH = os.getenv("VALIDATION_DATA_PATH")

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

@dag(
    dag_id='bi_encoder_training_pipeline',
    description='Полный ETL-пайплайн обучения bi-encoder модели',
    default_args=default_args,
    schedule_interval=None,
    start_date=days_ago(1),
    catchup=False,
    max_active_runs=1,
    tags=["bi-encoder", "training"]
)
def bi_encoder_training_dag():
    s3_sensor = S3KeySensor(
        task_id='wait_for_s3_file',
        bucket_name=S3_BUCKET,
        bucket_key=f"{S3_PREFIX}{S3_KEY}",
        aws_conn_id='aws_default',
        poke_interval=60,
        timeout=60 * 10,
        mode='poke'
    )

    @task()
    def download_data():
        import boto3
        s3 = boto3.client('s3')
        s3.download_file(S3_BUCKET, f"{S3_PREFIX}{S3_KEY}", LOCAL_DATA_PATH)
        print(f"Downloaded file from S3: {S3_BUCKET}/{S3_PREFIX}{S3_KEY} -> {LOCAL_DATA_PATH}")
        return LOCAL_DATA_PATH

    @task()
    def train_pipeline(local_data_path: str):
        metrics = run_pipeline(local_data_path, MODEL_SAVE_PATH, MODEL_NAME)
        return metrics

    @task()
    def check_metrics(metrics: dict):
        spearman = metrics.get("Spearman", 0)
        if spearman < METRICS_THRESHOLD:
            raise ValueError(f"Spearman {spearman:.4f} ниже порога {METRICS_THRESHOLD}. Pipeline остановлен.")
        else:
            print(f"Spearman {spearman:.4f} выше порога {METRICS_THRESHOLD}. Pipeline продолжается.")

    dvc_git_task = BashOperator(
        task_id='dvc_commit_git_push',
        bash_command=f"""
        set -e
        dvc pull
        dvc status -c
        dvc commit models/ || echo "No changes to commit"
        git add .
        git commit -m "Обновление модели через Airflow pipeline"
        git push
        dvc push
        """
    )

    local_path = download_data()
    metrics = train_pipeline(local_path)
    check_metrics(metrics) >> dvc_git_task

    s3_sensor >> local_path

bi_encoder_training_dag = bi_encoder_training_dag()
