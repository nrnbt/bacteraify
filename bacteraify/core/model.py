import joblib
import os
from django.http import HttpResponse
import pandas as pd
from docx import Document
import PyPDF2
import numpy as np
import hashlib
from datetime import datetime

model_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'model_jlib')
upload_file_path = os.path.dirname(os.path.dirname(__file__))

def save_file(file):
    _, file_extension = os.path.splitext(file.name)
    file_name = generate_hashed_filename()
    file_path = os.path.join(upload_file_path, 'survey-files' , file_name + file_extension)
    data = read_file(file)
    data.to_csv(file_path, index=False)
    return file_name

def read_file(file):
    _, file_extension = os.path.splitext(file.name)
        
    if file_extension == '.csv':
        data = read_csv(file)
    elif file_extension == '.xlsx':
        data = read_excel(file)
    elif file_extension == '.txt':
        data = read_text(file)
    elif file_extension == '.pdf':
        data = read_pdf(file)
    elif file_extension == '.docx':
        data = read_word(file)
    else:
        return HttpResponse("Unsupported file format")

    return data

def read_csv(file):
    data = pd.read_csv(file)
    return data

def read_excel(file):
    data = pd.read_excel(file)
    return data

def read_text(file, delimiter='\t'):
    data = pd.read_csv(file, delimiter)
    return data

def read_pdf(file):
    with open(file, 'rb') as file:
        pdf_reader = PyPDF2.PdfFileReader(file)
        text_data = ''
        for page_num in range(pdf_reader.numPages):
            text_data += pdf_reader.getPage(page_num).extractText()
    return text_data

def read_word(file):
    doc = Document(file)
    text_data = ''
    for paragraph in doc.paragraphs:
        text_data += paragraph.text + ' '
    return text_data

def generate_hashed_filename():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")

    hashed_timestamp = hashlib.sha256(timestamp.encode()).hexdigest()

    file_name = f"{hashed_timestamp}"

    return file_name

def predict(file):
  try:
    data = read_file(file)
    print('------------------------------ data ------------------------------\n', data, '\n')
    model = joblib.load(model_file_path)
    print('------------------------------ model ------------------------------\n', model, '\n')
    y_pred = model.predict(data)
    print('------------------------------ y_pred ------------------------------\n', y_pred, '\n')
    return ''

  except Exception as e:
    print(f"Error loading or predicting with the model: {e}")
    return None