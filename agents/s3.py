import boto3
import os
from dotenv import load_dotenv

load_dotenv()

S3_ID = os.getenv('AWS_ACCESS_KEY_ID')
S3_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

# Create an S3 Bucket
def create_bucket(bucket_name):
    s3 = boto3.client('s3', aws_access_key_id=S3_ID, aws_secret_access_key=S3_KEY)
    s3.create_bucket(Bucket=bucket_name)
    print("Succesfully created S3 Bucket")


if __name__ == "__main__":
    create_bucket('my-new-bucket-test-1094209421091')