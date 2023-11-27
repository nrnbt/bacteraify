# s3_utils.py

import boto3
import os

def download_model_from_s3(bucket_name, model_s3_path, local_model_path):
    s3 = boto3.client('s3',
                      aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                      aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])
    
    s3.download_file(bucket_name, model_s3_path, local_model_path)

def read_file_from_s3(key):
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    )
    response = s3_client.get_object(Bucket=os.environ.get('AWS_STORAGE_BUCKET_NAME '), Key=key)
    return response['Body'].read()