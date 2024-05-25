import boto3
from botocore.exceptions import NoCredentialsError
import os
import io
import pandas as pd
from datetime import datetime
import hashlib

def survey_upload_to_s3(request_file):
    S3_SURVEY_ACCESS_KEY_ID = os.environ.get('S3_SURVEY_ACCESS_KEY_ID')
    S3_SURVEY_SECRET_KEY_ID = os.environ.get('S3_SURVEY_SECRET_KEY_ID')
    S3_SURVEY_BUCKET_NAME = os.environ.get('S3_SURVEY_BUCKET_NAME')

    _, file_extension = os.path.splitext(request_file.name)

    s3 = boto3.client('s3', aws_access_key_id=S3_SURVEY_ACCESS_KEY_ID, aws_secret_access_key=S3_SURVEY_SECRET_KEY_ID)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    hashed_timestamp = hashlib.sha256(timestamp.encode()).hexdigest()
    file_name = f"{hashed_timestamp}"
    new_file_name = file_name + file_extension
    key = 'uploads/' + new_file_name
    fo = io.BytesIO(request_file.read())
    data_len = len(pd.read_csv(fo))
    fo.seek(0)
    
    try:
        s3.upload_fileobj(fo, S3_SURVEY_BUCKET_NAME, key)
        return new_file_name, data_len

    except NoCredentialsError:
        return "AWS credentials not available or incorrect"
    
def fetch_result_from_s3(file_key):
    try:
        aws_access_key_id=os.environ.get('S3_SURVEY_ACCESS_KEY_ID')
        aws_secret_access_key=os.environ.get('S3_SURVEY_SECRET_KEY_ID')
        aws_bucket_name=os.environ.get('S3_SURVEY_BUCKET_NAME')
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        response = s3_client.get_object(Bucket=aws_bucket_name, Key='results/'+file_key)
        file = response['Body'].read()
        buffered_reader = io.BufferedReader(io.BytesIO(file))
        return buffered_reader
    except Exception as e:
        print(f"Error reading file from S3: {e}")
        return None
    
def fetch_survey_from_s3(file_key):
    try:
        aws_access_key_id=os.environ.get('S3_SURVEY_ACCESS_KEY_ID')
        aws_secret_access_key=os.environ.get('S3_SURVEY_SECRET_KEY_ID')
        aws_bucket_name=os.environ.get('S3_SURVEY_BUCKET_NAME')
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        response = s3_client.get_object(Bucket=aws_bucket_name, Key='uploads/'+file_key)
        file = response['Body'].read()
        buffered_reader = io.BufferedReader(io.BytesIO(file))
        return buffered_reader
    except Exception as e:
        print(f"Error reading file from S3: {e}")
        return None