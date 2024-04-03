import os
import streamlit as st
import pandas as pd
from google.cloud import bigquery
from wordcloud import WordCloud
import matplotlib.pyplot as plt


# Get the database name from the environment variable set by Terraform
database_name = os.getenv("DATABASE_NAME")

# Initialize a BigQuery client
client = bigquery.Client()

# Set up the Streamlit app layout
st.title("Job Posting Analytics Dashboard")

# Input field for job title with a default value
default_job_title = "Data Engineer"
job_title_input = st.text_input("Enter a job title:", default_job_title)

# Function to fetch skills data from BigQuery
@st.cache_data
def fetch_skills_data(job_title, database_name):
    query = f"""
    WITH split_skills AS (
        SELECT job_title, SPLIT(job_skills, ',') AS skill
        FROM `{database_name}.linkedin_data`
        WHERE job_title LIKE '%{job_title}%'
    )
    SELECT skill, COUNT(*) AS skill_count
    FROM split_skills
    CROSS JOIN UNNEST(skill) AS skill
    GROUP BY skill
    ORDER BY skill_count DESC
    LIMIT 100;
    """
    query_job = client.query(query)
    results = query_job.result()
    return results.to_dataframe()

# Function to fetch company data from BigQuery
@st.cache_data
def fetch_companies_data(job_title, database_name):
    query = f"""
    SELECT company, COUNT(*) AS job_count
    FROM `{database_name}.linkedin_data`
    WHERE job_title LIKE '%{job_title}%'
    GROUP BY company
    ORDER BY job_count DESC
    """
    query_job = client.query(query)
    results = query_job.result()
    return results.to_dataframe()

# Fetching and displaying data
skills_df = fetch_skills_data(job_title_input, database_name)
companies_df = fetch_companies_data(job_title_input, database_name)

# Display header and results
st.header(f"Showing results for: '{job_title_input}' related jobs based on data processed from scraped dataset from LinkedIn in January 2024 (https://www.kaggle.com/datasets/asaniczka/1-3m-linkedin-jobs-and-skills-2024/)")

# Generate and display a word cloud
st.subheader("Skills Word Cloud")
word_cloud = WordCloud(width=800, height=400).generate_from_frequencies(dict(zip(skills_df["skill"], skills_df["skill_count"])))
fig, ax = plt.subplots()
ax.imshow(word_cloud, interpolation="bilinear")
ax.axis("off")
st.pyplot(fig)

# Display the top skills as a bar chart
st.subheader("Top 100 Skills Bar Chart")
st.bar_chart(skills_df.set_index("skill")["skill_count"])

# Display the data as a table
st.subheader("Top 100 Skills")
st.dataframe(skills_df)

# Display the top companies with the most job postings before selecting a specific company
st.subheader("Top 25 Companies by Job Postings")
st.table(companies_df.head(25))

# Company selection for a more detailed view
st.subheader("Jobs by Company - Select a company to see exact job entries (All posting companies are included)")
selected_company = st.selectbox("Select a company:", [""] + list(companies_df["company"].unique()))

if selected_company:
    # Display additional details for the selected company
    st.write(f"Showing details for {selected_company}:")
    # Note: The sum() is used to handle potential duplicates, it can be omitted if guaranteed only one row per company
    company_job_count = companies_df[companies_df["company"] == selected_company]["job_count"].sum()
    st.write(f"Total Job Postings: {company_job_count}")

    # Query and display job details for the selected company
    query = f"""
    SELECT job_title, job_location, job_level, job_type, last_processed_day, job_skills
    FROM `{database_name}.linkedin_data`
    WHERE job_title LIKE '%{job_title_input}%' AND company = '{selected_company}'
    LIMIT 100
    """
    job_details_df = client.query(query).result().to_dataframe()
    st.table(job_details_df)
else:
    # Display default table of companies if no specific selection is made
    st.table(companies_df.head(50))
