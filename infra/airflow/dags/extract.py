import airflow
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from operators.custom_operators import UnzipFileOperator

with DAG(dag_id="extract_and_load_into_spark", start_date=airflow.utils.dates.days_ago(1), schedule_interval=None, tags=['data_engineering', 'ingestion']) as dag:

    start = PythonOperator(
        task_id="start",
        python_callable=lambda: print("Jobs started"),
    )

    extract_task = UnzipFileOperator(
        task_id='extract_zip',
        zip_file_path='/opt/airflow/data/linkedin_data.zip',
        destination_folder='/opt/airflow/data',
    )

    python_job = SparkSubmitOperator(
        task_id="python_job",
        conn_id="spark-conn",
        application="jobs/python/wordcountjob.py",
    )

    end = PythonOperator(
        task_id="end",
        python_callable=lambda: print("Jobs completed successfully"),
    )

    start >> extract_task >> [python_job] >> end
