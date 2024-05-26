from celery import shared_task
from bacter_identification.models import Survey, TrainingData
import requests
import os
from django.utils import timezone
import logging

GPU_SERVER_URL = os.environ.get('GPU_SERVER_URL', 'localhost:8001')
logger = logging.getLogger(__name__)

@shared_task
def train_model_taskZ():
    try:
        surveys = Survey.objects.all()
        not_trained = 0
        for survey in surveys:
            file_name = survey.surveyFileName
            if not TrainingData.objects.filter(file_name=file_name).exists():
                not_trained += 1
                TrainingData.objects.create(file_name=file_name, status='not trained')

        print(f"---------------------------- {not_trained} record saved ---------------------------- \n")

        not_trained_data = TrainingData.objects.filter(status='not trained')
        not_trained_data_num = len(not_trained_data)
        if not_trained_data_num < 2:
            print(f"---------------------------- No trainable data returing ---------------------------- \n")
            return
        else:
            file_names = [data.file_name for data in not_trained_data]
            
            gpu_load_endpoint = GPU_SERVER_URL + 'model/train/'
            response = requests.post(gpu_load_endpoint, json={"file_names": file_names})
            if response.status_code == 200:
                data = response.json()
                trained_files = data['trained_files']
                print('trained_files', trained_files)
                for file_name in trained_files:
                    now = timezone.now()
                    TrainingData.objects.filter(file_name=file_name).update(status='trained', trained_at=now)
                print(f"---------------------------- {len(trained_files)} data trained ---------------------------- \n")

            else:
                print(f"Failed to send data. Status code: {response.status_code}")
    except Exception as e:
        logger.error(e)
        print('Error: ', e)
