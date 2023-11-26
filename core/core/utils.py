import os
import pandas as pd
from docx import Document
import PyPDF2
import hashlib
from datetime import datetime
from tensorflow.keras.models import load_model
import threading
# from channels.layers import get_channel_layer
# from asgiref.sync import async_to_sync
import logging
# import re
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from core.core.constants import model_file_path, STRAINS, upload_file_path
from core.core.survey import update_survey

from io import BytesIO
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from core.core.s3_utils import read_file_from_s3

from django.template.loader import get_template

logger = logging.getLogger(__name__)

def hash_user(regNo, phoneNo):
    return hashlib.sha256((regNo + phoneNo).encode()).hexdigest()

def save_file(file, directory_name):
    _, file_extension = os.path.splitext(file.name)
    file_name = generate_hashed_filename()
    file_path = os.path.join(upload_file_path, directory_name , file_name + file_extension)
    data = read_file(file)
    data.dropna(inplace=True)
    data.reset_index(drop=True, inplace=True)
    
    if not all(col.isdigit() for col in data.columns):
        headers = [f'{i+1}' for i in range(len(data.columns))] 
        # clean file data

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
    
def get_file_contents(fileName, dir):
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), dir, fileName + '.csv')
    with open(file_path, 'r') as file:
        return file.read()
    
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

# def notify_survey_result(data):
#     channel_layer = get_channel_layer()

#     async_to_sync(channel_layer.group_send) (
#         'survey_group',
#         {
#             'type': 'notify_survey_result',
#             'data': data
#         }
#     )

@require_POST
@csrf_exempt  # This is for simplicity. In production, use CSRF protection.
def notify_survey_result(request):
    try:
        file_name = request.POST.get('file_name')
        return JsonResponse({"message": "Notification sent successfully", "file_name": file_name})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


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
        # model = load_model(model_file_path)
        model = read_file_from_s3('model/cnn_model.h5')
        logger.info('------------------------------ model ------------------------------\n', model, '\n')
        y_pred = model.predict(data)
        logger.info('------------------------------ y_pred ------------------------------\n', y_pred, '\n')
        file_name = save_data_to_file(pd.DataFrame(y_pred), 'survey-results')

        update_survey(survey_file_name, result_file_name=file_name)

        # notify_survey_result({ "file_name": file_name })
    thread = threading.Thread(target=task)
    thread.start()
    return 'Prediction started'
  
  except Exception as e:
    logger.error(e)
    return None

def diff_graphic(title, y_data, x_data):
    fig, ax = plt.subplots(figsize=(10, 3))

    ax.plot(y_data, label='бодит')

    ax.plot(x_data, label='Таамагласан')

    ax.set_xlabel('Долгионы урт (нм)')
    ax.set_ylabel('Раманы Эрчим')
    ax.set_title(title)
    ax.legend()

    plt.tight_layout()

    with BytesIO() as buffer:
        plt.savefig(buffer, format='png')
        plt.close(fig)
        buffer.seek(0)
        image_png = buffer.getvalue()

        graphic = base64.b64encode(image_png)
        graphic = graphic.decode('utf-8')

        return graphic
    
def rendered_html(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    return html