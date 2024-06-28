import requests
import boto3
import json
from urllib.parse import urlparse
import streamlit as st
import streamlit_authenticator as stauth
import re
from io import BytesIO
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

S3_ID = os.getenv('S3_ID')
S3_KEY = os.getenv('S3_KEY')


def load_from_database(dataBucket, metadataBucket):
    with open('urls.json', 'r') as file:
        urls = json.load(file)

    for list_item in urls['url']:
        update_bucket(list_item, dataBucket, metadataBucket)
    

def download_html_and_create_json(url):
    response = requests.get(url)
    html_content = response.text

    parsed_url = urlparse(url)
    filename = re.sub(r'\W+', '_', parsed_url.netloc + parsed_url.path) + ".html"

    with open(filename, 'w') as file:
        file.write(html_content)

    url_data = {"url": url}

    with open(filename + '.json', 'w') as json_file:
        json.dump(url_data, json_file)
    
    return filename

def update_bucket(url, bucket_name, source_bucket):
    s3 = boto3.client('s3', aws_access_key_id=S3_ID, aws_secret_access_key=S3_KEY)
    
    response = requests.get(url)
    html_content = response.content

    parsed_url = urlparse(url)
    filename = re.sub(r'\W+', '_', parsed_url.netloc + parsed_url.path) + ".html"

    s3.put_object(Bucket=bucket_name, Key=filename, Body=html_content)

    url_data = {"url": url}
    json_content = json.dumps(url_data).encode('utf-8')  # Convert to bytes

    s3.put_object(Bucket=source_bucket, Key=filename + '.json', Body=BytesIO(json_content))

    return filename

st.title('HTML Downloader')

url = st.text_input('Enter the URL')

bucket = st.text_input('Enter the bucket name')
source = st.text_input('Enter the metadata bucket name')

if st.button("Load from Database"):
    load_from_database(bucket, source)

if st.button('Upload to S3 Bucket'):
    if url:
        filename = update_bucket(url, bucket, source)
        st.success(f'Downloaded and saved as {filename} and {filename}.json')
    else:
        st.error('Please enter a valid URL.')