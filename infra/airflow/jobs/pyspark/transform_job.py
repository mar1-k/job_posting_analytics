import pyspark
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, date_format
from pyspark.sql import functions as F


#Start spark session
spark = SparkSession.builder.appName("job_posting_analytics_spark_transformation").config("spark.executor.memory","8g").config("spark.driver.memory","8g").getOrCreate()

#Establish Dataframe, start with linkedin_job_postings.csv
df = spark.read.option("header", "true").option("inferSchema", "true").csv("gs://job-posting-analytics-testing-bucket/data/linkedin_job_postings.csv")
df = df.drop('is_being_worked')
df = df.withColumn("last_processed_day", date_format(col("last_processed_time"), "yyyy-MM-dd"))

#Read in the other csvs
df2 = spark.read.option("multiline", "true").option("header", "true").option("inferSchema", "true").csv("gs://job-posting-analytics-testing-bucket/data/job_skills.csv")
df3 = spark.read.option("multiline", "true").option("header", "true").option("inferSchema", "true").csv("gs://job-posting-analytics-testing-bucket/data/job_summary.csv")

#Join all three CSVs data into one big dataframe
df = df.join(df2, on='job_link', how='inner')
df = df.join(df3, on='job_link', how='inner')

#Partition the dataframe into parquet files
output_path = "gs://job-posting-analytics-testing-bucket/data/parquet/"
joined_df.repartition(20) \
  .write \
  .mode('overwrite') \
  .parquet(output_path)