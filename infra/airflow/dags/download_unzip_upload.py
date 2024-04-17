from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
import os

# Define the default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
with DAG(
    'ingest_to_datalake',
    default_args=default_args,
    description='A DAG to upload CSV files from a local directory to GCS',
    schedule_interval='@once',  # Run once as soon as possible
    start_date=datetime.now(),
    is_paused_upon_creation=False,
    tags=['data_engineering', 'ingestion', 'data_lake'],
) as dag:
    # Define the BashOperator to execute curl command to download the file
    download_task = BashOperator(
        task_id='execute_download_task',
        bash_command='curl -o /opt/airflow/data/2024_linkedin_scraped_data.zip https://storage.googleapis.com/project-raw-data/2024_linkedin_scraped_data.zip'
    )

    # Define the BashOperator to execute unzip command to unzip the file
    unzip_task = BashOperator(
        task_id='execute_unzip_task',
        bash_command='unzip -o /opt/airflow/data/2024_linkedin_scraped_data.zip -d /opt/airflow/data/'
    )

    # Define the LocalFilesystemToGCSOperator to upload the CSVs to the datalake
    upload_task = LocalFilesystemToGCSOperator(
        task_id="upload_job_to_gcs",
        bucket=os.environ.get("BUCKET_NAME"),
        src="/opt/airflow/data/*.csv",  # Upload all CSV files in the directory
        dst="data/"  # Destination directory in GCS
    )

    # Set the task dependencies
    download_task >> unzip_task >> upload_task
