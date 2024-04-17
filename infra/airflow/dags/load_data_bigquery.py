from datetime import timedelta, datetime
from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateExternalTableOperator
import os

PROJECT_ID = os.environ.get("PROJECT_ID")
BUCKET_NAME = os.environ.get("BUCKET_NAME")
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET")
GCS_DATA_PATH = 'data/parquet/'

# Define the default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the schema fields
schema = [
    {'name': 'job_link', 'type': 'STRING', 'mode': 'NULLABLE'},
    {'name': 'last_processed_time', 'type': 'STRING', 'mode': 'NULLABLE'},
    {'name': 'got_summary', 'type': 'STRING', 'mode': 'NULLABLE'},
    {'name': 'got_ner', 'type': 'STRING', 'mode': 'NULLABLE'},
    {'name': 'job_title', 'type': 'STRING', 'mode': 'NULLABLE'},
    {'name': 'company', 'type': 'STRING', 'mode': 'NULLABLE'},
    {'name': 'job_location', 'type': 'STRING', 'mode': 'NULLABLE'},
    {'name': 'first_seen', 'type': 'STRING', 'mode': 'NULLABLE'},
    {'name': 'search_city', 'type': 'STRING', 'mode': 'NULLABLE'},
    {'name': 'search_country', 'type': 'STRING', 'mode': 'NULLABLE'},
    {'name': 'search_position', 'type': 'STRING', 'mode': 'NULLABLE'},
    {'name': 'job_level', 'type': 'STRING', 'mode': 'NULLABLE'},
    {'name': 'job_type', 'type': 'STRING', 'mode': 'NULLABLE'},
    {'name': 'last_processed_day', 'type': 'STRING', 'mode': 'NULLABLE'},
    {'name': 'job_skills', 'type': 'STRING', 'mode': 'NULLABLE'},
    {'name': 'job_summary', 'type': 'STRING', 'mode': 'NULLABLE'},
]

# Define the DAG
with DAG(
    'load_data_to_bigquery',
    default_args=default_args,
    description='A DAG to load parquet files into BigQuery',
    schedule_interval=None,
    start_date=datetime(2023, 8, 1),  # Providing a fixed start date
    is_paused_upon_creation=False,
    tags=['data_engineering', 'load', 'BigQuery'],
) as dag:
    # Define the BigQueryCreateExternalTableOperator
    create_bq_external_table_task = BigQueryCreateExternalTableOperator(
        task_id='create_bq_external_table_task',
        destination_project_dataset_table=f"{BIGQUERY_DATASET}.linkedin_data",
        bucket=BUCKET_NAME,
        source_objects=[os.path.join(GCS_DATA_PATH, '*.parquet')],
        source_format='PARQUET',
        autodetect=False,  # Disable autodetection
        schema_fields=schema,  # Provide the schema manually
    )

    create_bq_external_table_task