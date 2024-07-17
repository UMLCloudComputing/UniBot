import requests
import boto3
import json
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import streamlit as st
import streamlit_authenticator as stauth
import re
from io import BytesIO
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

S3_ID = os.getenv('AWS_ACCESS_KEY_ID')
S3_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

S3_BUCKET = os.getenv('S3_BUCKET')

def ingest_data(knowledge_base, knowledge_source):
    client = boto3.client('bedrock-agent', aws_access_key_id=S3_ID, aws_secret_access_key=S3_KEY)
    response = client.start_ingestion_job(
        dataSourceId=knowledge_source,
        knowledgeBaseId=knowledge_base
    )

def load_from_database():
    with open('urls.json', 'r') as file:
        urls = json.load(file)

    for list_item in urls['urls']:
        update_bucket(list_item)

def update_bucket(url):

    bucket_name = S3_BUCKET

    s3 = boto3.client('s3', aws_access_key_id=S3_ID, aws_secret_access_key=S3_KEY)
    
    print("Succesfully created S3 Bucket")

    response = requests.get(url)
    html_content = response.content

    parsed_url = urlparse(url)
    filename = re.sub(r'\W+', '_', parsed_url.netloc + parsed_url.path) + ".html"

    s3.put_object(Bucket=bucket_name, Key=filename, Body=html_content)

    url_data = {"url": url}
    json_content = json.dumps(url_data).encode('utf-8')  # Convert to bytes

    s3.put_object(Bucket=bucket_name, Key=filename + '.json', Body=BytesIO(json_content))

    return filename


def streamlit():
    st.title('S3 Tools')

    url = st.text_input('Enter the URL')

    if st.button("Add URL directly to S3 Bucket"):
        update_bucket(url)

    if st.button("Add URL to database"):
        with open('urls.json', 'r') as file:
            data = json.load(file)
            data['urls'].append(url)
        
        with open('urls.json', 'w') as file:
            json.dump(data, file)
        
        st.success('URL added to database.')



    with open('urls.json', 'r') as file:
        data = json.load(file)
        
        urls = data['urls']

        with st.sidebar:
            st.write("### URLs from JSON file:")
            for index, url in enumerate(urls, start=1):
                st.write(f"{index}. {url}")

    if st.button("Load from Database"):
        load_from_database()


    st.title("Knowledge Base Ingestion")

    knowledge_base = st.text_input('Enter the knowledge base name')
    knowledge_source = st.text_input('Enter the knowledge base source ID')

    if st.button("Start Ingestion Job"):
        ingest_data(knowledge_base, knowledge_source)

if __name__ == '__main__':
    streamlit()