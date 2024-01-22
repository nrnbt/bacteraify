import os
import pandas as pd
from docx import Document
import PyPDF2
import hashlib
from datetime import datetime
from tensorflow.keras.models import load_model
import tensorflow as tf

from joblib import load
import threading
# from channels.layers import get_channel_layer
# from asgiref.sync import async_to_sync
import logging
# import re
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from core.core.constants import (
    CNN_MODEL_FILE_PATH,
    SVM_MODEL_FILE_PATH,
    RNN_MODEL_FILE_PATH,
    STRAINS,
    UPLOAD_FILE_PATH,
)
from core.core.survey import update_survey_cnn, update_survey_svm, update_survey_rnn

from io import BufferedReader, BytesIO
import base64
import matplotlib

import matplotlib.pyplot as plt
# from core.core.s3_utils import read_file_from_s3
from django.template.loader import get_template
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from core.core.types import FileDir

logger = logging.getLogger(__name__)

def hash_user(regNo: str, phoneNo: str) -> str:
    return hashlib.sha256((regNo + phoneNo).encode()).hexdigest()

class FileWriter:
    def __init__(self):
        self.upload_file_path = UPLOAD_FILE_PATH

    def save_file(self, file: UploadedFile, directory: FileDir) -> str:
        _, file_extension = os.path.splitext(file.name)
        file_name = self.generate_hashed_filename()
        file_path = os.path.join(
            self.upload_file_path, directory.value, file_name + file_extension
        )
        data_reader = FileContentReader(file)
        data = data_reader.read_file()
        data.dropna(inplace=True)
        data.reset_index(drop=True, inplace=True)

        if not all(col.isdigit() for col in data.columns):
            headers = [f"{i+1}" for i in range(len(data.columns))]
            # Clean file data

        data.to_csv(file_path, index=False)
        return file_name

    def save_df_to_file(self, data: pd.DataFrame, directory: FileDir) -> str:
        file_name = self.generate_hashed_filename()
        file_path = os.path.join(self.upload_file_path, directory.value, file_name + ".csv")
        data.to_csv(file_path, index=False)
        return file_name

    def generate_hashed_filename(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        hashed_timestamp = hashlib.sha256(timestamp.encode()).hexdigest()
        file_name = f"{hashed_timestamp}"
        return file_name

class FileReader:
    def __init__(self):
        self.UPLOAD_FILE_PATH = UPLOAD_FILE_PATH

    def get_file_contents(self, file_name: str, directory: FileDir) -> (pd.DataFrame | None):
        file_path = os.path.join(self.UPLOAD_FILE_PATH, directory.value, file_name + ".csv")
        if os.path.isfile(file_path):
            file_reader = FileContentReader(open(file_path, "rb"))
            result = file_reader.read_file()
            return result
        else:
            raise FileNotFoundError("File not found")

    def get_file(self, file_name, directory):
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), directory.value, file_name + ".csv")
        with open(file_path, "r") as file:
            return file.read()

class FileContentReader:
    def __init__(self, file: BufferedReader) -> (pd.DataFrame | None):
        self.file = file

    def read_file(self):
        _, file_extension = os.path.splitext(self.file.name)
        if file_extension == ".csv":
            data = self.read_csv()
        elif file_extension == ".xlsx":
            data = self.read_excel()
        elif file_extension == ".txt":
            data = self.read_text()
        elif file_extension == ".pdf":
            data = self.read_pdf()
        elif file_extension == ".docx":
            data = self.read_word()
        else:
            raise TypeError("Unsupported file format")
        return data

    def read_csv(self) -> pd.DataFrame:
        data = pd.read_csv(self.file)
        return data

    def read_excel(self) -> pd.DataFrame:
        data = pd.read_excel(self.file)
        return data

    def read_text(self, delimiter="\t"):
        data = pd.read_csv(self.file, delimiter)
        return data

    def read_pdf(self) -> pd.DataFrame:
        with open(self.file, "rb") as file:
            pdf_reader = PyPDF2.PdfFileReader(file)
            text_data = ""
            for page_num in range(pdf_reader.numPages):
                text_data += pdf_reader.getPage(page_num).extractText()
        return text_data

    def read_word(self) -> pd.DataFrame:
        doc = Document(self.file)
        text_data = ""
        for paragraph in doc.paragraphs:
            text_data += paragraph.text + " "
        return text_data

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
        file_name = request.POST.get("file_name")
        return JsonResponse(
            {"message": "Notification sent successfully", "file_name": file_name}
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

class Predictor:

    def predict(self, data: pd.DataFrame, survey_file_name: str, model_types: list):
        try:
            def task():
                file_writer = FileWriter()
                model_types_len = len(model_types)
                for index, char in enumerate(model_types):
                    if char == "CNN":
                        if hasattr(tf, "executing_eagerly_outside_functions"):
                            tf.compat.v1.executing_eagerly_outside_functions = (tf.executing_eagerly_outside_functions)
                            del tf.executing_eagerly_outside_functions
                        path = CNN_MODEL_FILE_PATH
                        model = load_model(path)
                        logger.info("------------------------------ CNN MODEL ------------------------------\n", model, "\n")
                        y_pred = model.predict(data)
                        logger.info("--------------------------- CNN MODEL Y_PRED ---------------------------\n", y_pred, "\n")
                        file_name = file_writer.save_df_to_file(pd.DataFrame(y_pred), FileDir.RESULT)
                        status = f"{index + 1}/{model_types_len} predicted"
                        update_survey_cnn(survey_file_name, status=status, file_name=file_name)
                    elif char == "SVM":
                        path = SVM_MODEL_FILE_PATH
                        model = load(path)
                        X_test = data.values if isinstance(data, pd.DataFrame) else data
                        logger.info("------------------------------ SVM MODEL ------------------------------\n", model, "\n")
                        y_pred = model.predict(X_test)
                        y_pred_probabilities = model.predict_proba(X_test)
                        logger.info("--------------------------- SVM MODEL Y_PRED ---------------------------\n", y_pred, "\n")
                        file_name = file_writer.save_df_to_file(pd.DataFrame(y_pred_probabilities), FileDir.RESULT)
                        status = f"{index + 1}/{model_types_len} predicted"
                        update_survey_svm(survey_file_name, status=status, file_name=file_name)
                    elif char == "RNN":
                        path = RNN_MODEL_FILE_PATH
                        model = load_model(path)
                        logger.info("------------------------------ RNN MODEL ------------------------------\n", model, "\n")
                        y_pred = model.predict(data)
                        logger.info("--------------------------- RNN MODEL Y_PRED ---------------------------\n",y_pred,"\n")
                        file_name = file_writer.save_df_to_file(pd.DataFrame(y_pred), FileDir.RESULT)
                        status = f"{index + 1}/{model_types_len} predicted"
                        update_survey_rnn(survey_file_name, status=status, file_name=file_name)
                    else:
                        logger.warning("Invalid model type")

            thread = threading.Thread(target=task)
            thread.start()
            return "Prediction started"

        except Exception as e:
            logger.error(e)
            return None
        
    def process_prediction_result(self, model_types: list, cnn: str, svm: str, rnn: str) -> list:
        file_reader = FileReader()
        
        data = {}
        for char in model_types:
            if char == 'CNN':
                data[char] = file_reader.get_file_contents(cnn, FileDir.RESULT) 
            elif char == 'SVM':
                data[char] = file_reader.get_file_contents(svm, FileDir.RESULT) 
            elif char == 'RNN':
                data[char] = file_reader.get_file_contents(rnn, FileDir.RESULT)

        result_by_model_key = {}
        for key, value in data.items():
            result = {}
            prediction = value.values
            predicted_percentages = prediction * 100
            for class_label, percentage in enumerate(predicted_percentages[0]):
                if percentage > 1:
                    bacteria_name = STRAINS[class_label]
                    result.update({f"{bacteria_name}": f"{percentage:.4f}%"})
            logger.info("---------------------------- result_data ----------------------------\n", result, "\n")
            result = dict(sorted(result.items(), key=lambda item: float(item[1].rstrip("%")), reverse=True))
            result_by_model_key[key] = result

        combined_table_data = {}
        for algorithm, data in result_by_model_key.items():
            for bacteria, percentage in data.items():
                if bacteria not in combined_table_data:
                    combined_table_data[bacteria] = {'bacteria': bacteria}
                combined_table_data[bacteria][algorithm] = percentage

        return list(combined_table_data.values())
        
class GraphicGenerator:
    def __init__(self):
        matplotlib.use("Agg")

    def create_graphic(self, title, y_data, x_data=None):
        fig, ax = plt.subplots(figsize=(10, 3))
        ax.plot(y_data, label="бодит")
        
        if x_data:
            ax.plot(x_data, label="Таамагласан")

        ax.set_xlabel("Долгионы урт (нм)")
        ax.set_ylabel("Раманы Эрчим")
        ax.set_title(title)
        ax.legend()
        plt.tight_layout()

        with BytesIO() as buffer:
            plt.savefig(buffer, format="png")
            plt.close(fig)
            buffer.seek(0)
            image_png = buffer.getvalue()
            graphic = base64.b64encode(image_png)
            graphic = graphic.decode("utf-8")
            return graphic

def rendered_html(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    return html

def encode_image_to_base64(image_relative_path):
    image_path = os.path.join(settings.BASE_DIR, "core/static", image_relative_path)
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
        return encoded_string.decode("utf-8")
    
class TestDataReader:
    def __init__(self):
        self.upload_file_path = UPLOAD_FILE_PATH

    def get_test_x_data_file(self, index):
        file_path = os.path.join(self.upload_file_path, FileDir.TEST_SURVEY.value, str(index) + "_x.csv")
        with open(file_path, "r") as file:
            return file.read()

    def get_test_file(self, index):
        file_path = os.path.join(self.upload_file_path, FileDir.TEST_SURVEY_RESULT.value, str(index) + "_y.csv")

        if os.path.isfile(file_path):
            data_reader = FileContentReader(open(file_path, "rb"))
            result = data_reader.read_file()
            return result
        else:
            raise FileNotFoundError("File not found")

