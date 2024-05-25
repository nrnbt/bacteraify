import boto3
from botocore.exceptions import NoCredentialsError
import os
from main.core.utils import FileWriter
import io
import pandas as pd

def survey_upload_to_s3(request_file):
    S3_SURVEY_ACCESS_KEY_ID = os.environ.get('S3_SURVEY_ACCESS_KEY_ID')
    S3_SURVEY_SECRET_KEY_ID = os.environ.get('S3_SURVEY_SECRET_KEY_ID')
    S3_SURVEY_BUCKET_NAME = os.environ.get('S3_SURVEY_BUCKET_NAME')

    _, file_extension = os.path.splitext(request_file.name)

    s3 = boto3.client('s3', aws_access_key_id=S3_SURVEY_ACCESS_KEY_ID, aws_secret_access_key=S3_SURVEY_SECRET_KEY_ID)
    new_file_name = FileWriter().generate_hashed_filename() + file_extension
    key = 'uploads/' + new_file_name
    fo = io.BytesIO(request_file.read())
    data_len = len(pd.read_csv(fo))

    try:
        s3.upload_fileobj(fo, S3_SURVEY_BUCKET_NAME, key)
        return new_file_name, data_len

    except NoCredentialsError:
        return "AWS credentials not available or incorrect"
    
def result_upload_to_s3(request_file):
  S3_SURVEY_ACCESS_KEY_ID = os.environ.get('S3_SURVEY_ACCESS_KEY_ID')
  S3_SURVEY_SECRET_KEY_ID = os.environ.get('S3_SURVEY_SECRET_KEY_ID')
  S3_SURVEY_BUCKET_NAME = os.environ.get('S3_SURVEY_BUCKET_NAME')

  s3 = boto3.client('s3', aws_access_key_id=S3_SURVEY_ACCESS_KEY_ID, aws_secret_access_key=S3_SURVEY_SECRET_KEY_ID)
  new_file_name = FileWriter().generate_hashed_filename() + '.csv'
  key = 'result/' + new_file_name
  fo = io.BytesIO(request_file.read())
  data_len = len(pd.read_csv(fo))

  try:
      s3.upload_fileobj(fo, S3_SURVEY_BUCKET_NAME, key)
      return new_file_name, data_len

  except NoCredentialsError:
      return "AWS credentials not available or incorrect"

