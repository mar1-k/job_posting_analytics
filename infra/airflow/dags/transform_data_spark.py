from datetime import timedelta, datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.providers.google.cloud.operators.dataproc import DataprocSubmitJobOperator, DataprocDeleteClusterOperator
from airflow.operators.dagrun_operator import TriggerDagRunOperator
import os

GOOGLE_CONN_ID = "google_cloud_default"
PROJECT_ID = os.environ.get("PROJECT_ID")
BUCKET_NAME = os.environ.get("BUCKET_NAME")
CLUSTER_NAME = os.environ.get("CLUSTER_NAME")
REGION = os.environ.get("REGION")
PYSPARK_JOB_PATH = '/opt/airflow/jobs/pyspark/transform_data.py'
GCS_JOB_PATH = 'pyspark_jobs/transform_data.py'


def create_pyspark_job_file():
    # Define the path where the job file will be created
    file_path = PYSPARK_JOB_PATH

    # Define the content of the PySpark job script
    file_content = f"""
import pyspark
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, date_format
from pyspark.sql import functions as F

# Start spark session
spark = SparkSession.builder.appName("job_posting_analytics_spark_transformation").config("spark.executor.memory","8g").config("spark.driver.memory","8g").getOrCreate()

# Establish Dataframe, start with linkedin_job_postings.csv
df = spark.read.option("header", "true").option("inferSchema", "true").csv("gs://{BUCKET_NAME}/data/linkedin_job_postings.csv")
df = df.drop('is_being_worked')
df = df.withColumn("last_processed_day", date_format(col("last_processed_time"), "yyyy-MM-dd"))

# Read in the other csvs
df2 = spark.read.option("multiline", "true").option("header", "true").option("inferSchema", "true").csv("gs://{BUCKET_NAME}/data/job_skills.csv")
df3 = spark.read.option("multiline", "true").option("header", "true").option("inferSchema", "true").csv("gs://{BUCKET_NAME}/data/job_summary.csv")

# Join all three CSVs data into one big dataframe
df = df.join(df2, on='job_link', how='inner')
df = df.join(df3, on='job_link', how='inner')

# Partition the dataframe into parquet files for better ingestion into BQ
output_path = "gs://{BUCKET_NAME}/data/parquet/"
df.repartition(20) \\
    .write \\
    .mode('overwrite') \\
    .parquet(output_path)
"""

    # Write the content to the file
    with open(file_path, 'w') as file:
        file.write(file_content)

    print(f"File created at {file_path}")

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
    'transform_data_with_spark',
    default_args=default_args,
    description='A DAG to process CSVs with PySpark',
    schedule_interval=None, 
    start_date=datetime.now(),
    is_paused_upon_creation=False,
    tags=['data_engineering', 'transform', 'PySpark'],
) as dag:
        
    # Task to create the job file
    create_job_file_task = PythonOperator(
        task_id='create_job_file_task',
        python_callable=create_pyspark_job_file
    )

    # Task to upload the PySpark job to GCS
    upload_job_to_gcs_task = LocalFilesystemToGCSOperator(
        bucket = BUCKET_NAME,
        task_id='upload_job_to_gcs_task',
        src=PYSPARK_JOB_PATH,
        dst=GCS_JOB_PATH
    )
    
    # Task to submit the PySpark job to Dataproc
    submit_pyspark_task = DataprocSubmitJobOperator(
        task_id='submit_pyspark_task',
        job={
            "reference": {"project_id": PROJECT_ID},
            "placement": {"cluster_name": CLUSTER_NAME},
            "pyspark_job": {
                "main_python_file_uri": f"gs://{BUCKET_NAME}/{GCS_JOB_PATH}",
            },
        }, 
        region=REGION,
        project_id=PROJECT_ID,
    )

    # Task to delete the dataproc cluster so we can save our GCP bucks
    delete_dataproc_cluster_task = DataprocDeleteClusterOperator(
        task_id = 'delete_dataproc_cluster_task',
        project_id = PROJECT_ID,
        region = REGION,
        cluster_name = CLUSTER_NAME
    )
    
    # Define the TriggerDagRunOperator to trigger the load DAG
    trigger_bq_load_dag_task = TriggerDagRunOperator(
        task_id = 'trigger_bq_load_dag_task',
        trigger_dag_id = 'load_data_to_bigquery'
    )


    # Define task dependencies
    create_job_file_task >> upload_job_to_gcs_task >> submit_pyspark_task >> delete_dataproc_cluster_task >> trigger_bq_load_dag_task
