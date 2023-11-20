import os
from django.http import HttpResponse
import pandas as pd
from docx import Document
import PyPDF2
import numpy as np
import hashlib
from datetime import datetime
from tensorflow.keras.models import load_model
import threading
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from bacter_identification.models import Survey
import logging

logger = logging.getLogger(__name__)
model_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'cnn_model.h5')
upload_file_path = os.path.dirname(os.path.dirname(__file__))

colors = [
    'rgba(83, 169, 112, 0.2)',
    'rgba(27, 174, 131, 0.2)',
    'rgba(200, 95, 136, 0.2)',
    'rgba(230, 83, 183, 0.2)',
    'rgba(68, 18, 116, 0.2)',
    'rgba(53, 1, 98, 0.2)',
    'rgba(57, 76, 23, 0.2)',
    'rgba(1, 212, 84, 0.2)',
    'rgba(74, 120, 93, 0.2)',
    'rgba(165, 74, 177, 0.2)',
    'rgba(225, 153, 236, 0.2)',
    'rgba(202, 153, 246, 0.2)',
    'rgba(210, 17, 149, 0.2)',
    'rgba(132, 11, 131, 0.2)',
    'rgba(123, 163, 59, 0.2)',
    'rgba(226, 112, 15, 0.2)',
    'rgba(135, 241, 131, 0.2)',
    'rgba(254, 200, 22, 0.2)',
    'rgba(75, 90, 148, 0.2)',
    'rgba(122, 234, 64, 0.2)',
    'rgba(128, 169, 181, 0.2)',
    'rgba(92, 218, 238, 0.2)',
    'rgba(248, 64, 155, 0.2)',
    'rgba(117, 245, 28, 0.2)',
    'rgba(51, 187, 7, 0.2)',
    'rgba(45, 73, 173, 0.2)',
    'rgba(59, 217, 7, 0.2)',
    'rgba(108, 58, 101, 0.2)',
    'rgba(123, 186, 130, 0.2)',
    'rgba(34, 79, 30, 0.2)'
]

STRAINS = {
    0: "C. albicans",
    1: "C. glabrata",
    2: "K. aerogenes",
    3: "E. coli 1",
    4: "E. coli 2",
    5: "E. faecium",
    6: "E. faecalis 1",
    7: "E. faecalis 2",
    8: "E. cloacae",
    9: "K. pneumoniae 1",
    10: "K. pneumoniae 2",
    11: "P. mirabilis",
    12: "P. aeruginosa 1",
    13: "P. aeruginosa 2",
    14: "MSSA 1",
    15: "MSSA 3",
    16: "MRSA 1 (isogenic)",
    17: "MRSA 2",
    18: "MSSA 2",
    19: "S. enterica",
    20: "S. epidermidis",
    21: "S. lugdunensis",
    22: "S. marcescens",
    23: "S. pneumoniae 2",
    24: "S. pneumoniae 1",
    25: "S. sanguinis",
    26: "Group A Strep.",
    27: "Group B Strep.",
    28: "Group C Strep.",
    29: "Group G Strep.",
}

def save_file(file, directory_name):
    _, file_extension = os.path.splitext(file.name)
    file_name = generate_hashed_filename()
    file_path = os.path.join(upload_file_path, directory_name , file_name + file_extension)
    data = read_file(file)
    data.to_csv(file_path, index=False)
    return file_name

def save_data_to_file(data, directory_name):
    file_name = generate_hashed_filename()
    file_path = os.path.join(upload_file_path, directory_name , file_name + '.csv')
    data.to_csv(file_path, index=False)
    return file_name

def get_file(file_name, directory):
    file_path = os.path.join(upload_file_path, directory , file_name + '.csv')
    if os.path.isfile(file_path):
        result = read_file(open(file_path, 'rb'))
        return result
    else:
        return 'File not found'
    
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

def notify_survey_result(data):
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send) (
        'survey_group',
        {
            'type': 'notify_survey_result',
            'data': data
        }
    )

def process_result_data(prediction):
    result = {}
    predicted_percentages = prediction * 100
    for class_label, percentage in zip(range(len(predicted_percentages[0])), predicted_percentages[0]):
        if percentage > 0.1:
            bacteria_name = STRAINS[class_label]
            # result.update({ f'{bacteria_name} (Class {class_label})': f'{percentage:.4f}%' })
            result.update({ f'{bacteria_name}': f'{percentage:.4f}%' })
    logger.info('---------------------------- result_data ----------------------------\n', result, '\n')

    sorted_bacteria_counts_desc = dict(sorted(result.items(), key=lambda item: float(item[1].rstrip('%')), reverse=True))

    return sorted_bacteria_counts_desc

def predict(data, survey_file_name):
  try:
    def task():
        model = load_model(model_file_path)
        logger.info('------------------------------ model ------------------------------\n', model, '\n')
        y_pred = model.predict(data)
        logger.info('------------------------------ y_pred ------------------------------\n', y_pred, '\n')
        file_name = save_data_to_file(pd.DataFrame(y_pred), 'survey-results')

        update_record(survey_file_name, result_file_name=file_name)

        notify_survey_result({ "file_name": file_name })
    thread = threading.Thread(target=task)
    thread.start()
    return 'Prediction started'
  
  except Exception as e:
    logger.error(e)
    return None
  

def save_record(user_id, user_email, file_name, data_len):
    survey_record = Survey(
        userId = user_id,
        userEmail = user_email,
        surveyFileName = file_name,
        rowNumber = data_len,
        type = 'created'
    )
    survey_record.save()

def update_record(survey_file_name, result_file_name):
    survey = Survey.objects.get(surveyFileName=survey_file_name)
    survey.resultFileName = result_file_name
    survey.type = 'predicted'
    survey.save()