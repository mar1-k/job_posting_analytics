# job_posting_analytics

A Data Engineering project for visualizing the top skills demanded by roles based on the batch parsing of scraped LinkedIn job postings.

## Description

### Objective

Creation of a fully orchestrated batch data pipeline and a dashboard app for interacting with the raw scraped LinkedIn job data in order to gain insights regarding in demand skills for jobs.

### Dataset

I am utilizing the following '1.3M Linkedin Jobs & Skills (2024)' dataset from Kaggle. https://www.kaggle.com/datasets/asaniczka/1-3m-linkedin-jobs-and-skills-2024/

The dataset is comprised of 3 csvs containing 1.3 million rows of scraped job data from LinkedIn from January 2024:

- linkedin_job_postings.csv
- job_skills.csv
- job_summary.csv

### Tools and Technologies

- Cloud - [**Google Cloud Platform**](https://cloud.google.com)
- Infrastructure as Code software - [**Terraform**](https://www.terraform.io)
- Containerization - [**Docker**](https://www.docker.com), [**Docker Compose**](https://docs.docker.com/compose/)
- Orchestration - [**Apache Airflow**](https://airflow.apache.org)
- Transformation and Batch Processing - [**Apache Spark**](https://spark.apache.org/)
- Data Lake - [**Google Cloud Storage**](https://cloud.google.com/storage)
- Data Warehouse - [**BigQuery**](https://cloud.google.com/bigquery)
- Data Visualization - [**Streamlit**](https://streamlit.io/)
- Dashboard App Deploymment - [**Cloud Run**](https://cloud.google.com/run)
- Language - [**Python**](https://www.python.org)

### Architecture
![image](https://github.com/mar1-k/job_posting_analytics/assets/14811869/48bfa625-95a7-4d89-8aed-4ef23114fe1f)

### Final Result

A live version of the dashboard app can be accessed at: https://streamlit-dashboard-ucsfwi2asq-uc.a.run.app/

![dashboard](https://github.com/mar1-k/job_posting_analytics/assets/14811869/b346893f-caa0-460b-ab7c-f63c2e7fb956)
![dashboard2](https://github.com/mar1-k/job_posting_analytics/assets/14811869/8eca8846-8f38-4501-9ec1-0373194e50a0)


### Getting started with running your own version of this project:

See [deploy.md](https://github.com/mar1-k/job_posting_analytics/blob/main/infra/deploy.md)

### Mentions and Credits

This has been a capstone project for the 2024 cohort of [DataTalks.Club](https://datatalks.club) Data Engineering Zoomcamp. I am deeply grateful to [Alexey Grigorev](https://github.com/alexeygrigorev) and the team for making this quality course available completely free and painstaklingly going through the effort of making it all possible. 

Since the 2024 cohort of the Zoomcamp primarily utilized Mage for orchestration and I chose to go with Airflow for this project, I benefited a lot from these two projects for my Airflow deployment. So a thank you to [Ankur Chavda](https://github.com/ankurchavda/) and [Yusuf Ganiyu](https://github.com/airscholar)
- https://github.com/ankurchavda/streamify
- https://github.com/airscholar/SparkingFlow

I would also like to thank [Asaniczka](https://www.kaggle.com/asaniczka) of course for the Dataset that made this project possible.
