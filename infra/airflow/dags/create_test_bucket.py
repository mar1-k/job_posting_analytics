from datetime import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.google.cloud.operators.storage import GCSCreateBucketOperator
from airflow.models import Variable

# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 4, 17),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
with DAG('create_gcp_bucket', 
         default_args=default_args, 
         schedule_interval=None, 
         catchup=False) as dag:

    # Task to create GCP bucket
    create_bucket_task = GCSCreateBucketOperator(
        task_id='create_bucket',
        bucket_name='test_bucket',
        project_id=Variable.get('google_cloud_project_id'),
        location='us-central1',
        gcp_conn_id='google_cloud_default',  # Using the Google Cloud Platform connection
        labels={"env": "dev"}
    )

    # Define the task dependencies
    create_bucket_task
