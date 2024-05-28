from django.shortcuts import render
from django.shortcuts import redirect
import os
from django.contrib import messages
from bacter_identification.models import Survey, Bacteria, ClassificationResult, TrainingData
import logging
from django.http import Http404, JsonResponse, HttpResponse
import pandas as pd
from io import StringIO
from main.core.utils import hash_user, Predictor, TestDataReader, GraphicGenerator, rendered_html, encode_image_to_base64
from main.core.survey import create_survey, survey_result_available, filter_survey_by_hash
from main.core.constants import COLORS, STRAINS
from main.forms import SurveyForm, SurveySearchForm
import json
import numpy as np
from datetime import datetime, timedelta
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from main.core.file_handler import survey_upload_to_s3, fetch_survey_from_s3
import requests
from django.utils import timezone

GPU_SERVER_URL = os.environ.get('GPU_SERVER_URL', 'localhost:8001')

logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'pages/index.html')

def survey(request):
    context = { 'strains': [STRAINS[key] for key in STRAINS] }
    return render(request, 'pages/survey.html', context)

def faq(request):
    return render(request, 'pages/faq.html')

def more(request):
    return render(request, 'pages/more.html')

def upload_survey(request):
    try:
        if request.method == 'POST':
            form = SurveyForm(request.POST, request.FILES)
            if form.is_valid():
                phone_no = form.cleaned_data['phone_no']
                reg_no = form.cleaned_data['reg_no'].upper()
                file = form.cleaned_data['file']
                model_types = form.cleaned_data['model_types']
                file_name, data_len = survey_upload_to_s3(file)
                
                if file_name:
                    survey_id = create_survey(
                        user_id=request.user.id, 
                        user_email= request.user.email,
                        file_name=file_name, 
                        data_len=data_len,
                        patient_hash=hash_user(reg_no, phone_no),
                        model_types = model_types,
                        merch_id=request.user.merchant_id
                    )

                    return redirect('/survey/load/?id={}'.format(survey_id))
                else:
                    messages.error(request, 'Error: Something went wrong!', {'form': form})
                    return render(request, 'pages/survey.html')
            else:
                for field, errors in form.errors.items():
                    messages.error(request, errors)
                    return render(request, 'pages/survey.html',  {'form': form})
        else:
            return render(request, 'pages/survey.html')
    except Exception as e:
        logger.error(e)
        messages.error(request, 'Error: Something went wrong!')
        return render(request, 'pages/survey.html', {'form': form if form else SurveyForm()})

def load_model(request):
    try:
        survey_id = request.GET.get('id')
        employee_id = request.user.id
        merch_id = request.user.merchant_id

        result =  ClassificationResult(
            survey_id = survey_id,
            merch_id = merch_id,
            employee_id = employee_id
        )
        survey = Survey.objects.get(id=survey_id)
        predicted = survey_result_available(survey.status)
        predicted=False
        if predicted:
            return redirect('/survey/result/?id={}'.format(survey_id))
        else:
            cnn = False
            svm = False
            modelTypes = survey.modelTypes
            file_name = survey.surveyFileName
            if 'CNN' in modelTypes:
                cnn = True
            if 'SVM' in modelTypes:
                svm = True

            payload = {
                'survey_file_name': file_name,
                'CNN': cnn,
                'SVM': svm,
            }

            gpu_load_endpoint = GPU_SERVER_URL + 'survey/load/'
            response = requests.post(gpu_load_endpoint, json=payload)
            data = response.json()
            predictor = Predictor()
            results_via_gpu_server = data['prediction_result_file_names']
            if results_via_gpu_server is None:
                data = pd.read_csv(fetch_survey_from_s3(file_name))
                predictor.predict(data, survey_file_name=file_name, model_types=modelTypes, result=result)
            else:
                predictor.process_data_from_gpu_server(
                    prediction_result_file_names=results_via_gpu_server, 
                    model_types=modelTypes,
                    survey_file_name=file_name,
                    result=result
                )

            return render(request, 'pages/survey.html', { 'id': survey_id })
    except Survey.DoesNotExist:
        raise Http404("Survey does not exist")
    except Exception as e:
        logger.error(e)
        messages.error(request, 'Error: Something went wrong!')
    return render(request, 'pages/survey.html')

def survey_result(request):
    try:
        survey_id = request.GET.get('id')
        survey = Survey.objects.filter(id=survey_id).values('surveyFileName', 'modelTypes', 'status', 'cnnPredFileName', 'svmPredFileName', 'rnnPredFileName').first()
        model_types = survey['modelTypes']

        predictor = Predictor()
        result_data = predictor.survey_result_data_from_s3(
            model_types=model_types,
            cnn=survey['cnnPredFileName'],
            svm=survey['svmPredFileName'],
            rnn=survey['rnnPredFileName']
        )
        result_by_percentage = predictor.process_prediction_result(result_data)
        context = {
            'result_data': result_by_percentage,
            'model_types': model_types,
            'colors': COLORS
        }

        return render(request, 'pages/survey.html', context)
    except Exception as e:
        logger.error(e)
        messages.error(request, 'Error: Something went wrong!')
    return render(request, 'pages/survey.html')

def surveys(request):
    try:
        surveys_list  = Survey.objects.filter(userId=request.user.id).order_by('-created_at')
        surveys_per_page = 10

        paginator = Paginator(surveys_list, surveys_per_page)
        page = request.GET.get('page')

        try:
            surveys = paginator.page(page)
        except PageNotAnInteger:
            surveys = paginator.page(1)
        except EmptyPage:
            surveys = paginator.page(paginator.num_pages)
        context = {'surveys': surveys}

    except Exception as e:
        logger.error(e)
        messages.error(request, 'Error: Something went wrong!')
    return render(request, 'pages/surveys.html', context)

def download_survey(request):
    survey_id = request.GET.get('id')
    survey = Survey.objects.filter(id=survey_id).values('modelTypes', 'cnnPredFileName', 'svmPredFileName', 'rnnPredFileName', 'created_at', 'surveyNumber', 'surveyFileName').first()
    predictor = Predictor()

    try:
        if survey_id is not None:
            model_types = survey['modelTypes']
            result_data = predictor.survey_result_data_from_s3(
                model_types=model_types,
                cnn=survey['cnnPredFileName'],
                svm=survey['svmPredFileName'],
                rnn=survey['rnnPredFileName']
            )
            result_by_percentage = predictor.process_prediction_result(result_data)
            process_result_data_v2_data = predictor.process_result_data_v2(result_data)
            parsed_date = datetime.strptime(str(survey['created_at']), '%Y-%m-%d %H:%M:%S.%f%z')
            formatted_date = parsed_date.strftime('%Y-%m-%d %H:%M:%S')
            graphic_generator = GraphicGenerator()
            bacteria_list = [item['bacteria'] for item in process_result_data_v2_data]
            bacteria_graphics = graphic_generator.get_predicted_graphic_v2(
                bacteria_list, 
                survey['surveyFileName']
            )
            encoded_logo_img = encode_image_to_base64('images/brand-logo.png')
            context = {
                'created_at': formatted_date,
                'logo_img_data': encoded_logo_img,
                'model_types': model_types,
                'number': survey['surveyNumber'],
                'result_data': result_by_percentage,
                'bacteria_images': bacteria_graphics,
                'BASE_URL': os.environ.get('BASE_URL', 'http://127.0.0.1:8000')
            }

            resp_data = rendered_html('pages/survey-result-pdf.html', context)
            res = json.dumps({
                'resp_data': resp_data, 'survey_number': survey['surveyNumber']
            })
            return HttpResponse(res, content_type="application/json")
        
        else:
            messages.error(request, 'Error: Something went wrong!')
            return Http404("Survey not provided")

    except Exception as e:
        logger.error(e)
        messages.error(request, 'Error: Something went wrong!')
        return render(request, 'pages/surveys.html')

def check_survey_result(request, id=None):
    if id is not None:
        survey = Survey.objects.filter(id=id).values('status').first()
        predicted = survey_result_available(survey['status'])
        if predicted:
            return JsonResponse({"id": id})
        else:
            return JsonResponse({"error": 'result not found'})
    else:
        return JsonResponse({"error": 'survey not found'})

def survey_result_pdf_view(request):
    survey_id = request.GET.get('id')
    survey = Survey.objects.filter(id=survey_id).values('modelTypes', 'cnnPredFileName', 'svmPredFileName', 'rnnPredFileName', 'created_at', 'surveyNumber', 'surveyFileName').first()
    predictor = Predictor()

    try:
        if survey_id is not None:
            result_data = predictor.suvrey_result_data(
                model_types=survey['modelTypes'],
                cnn=survey['cnnPredFileName'],
                svm=survey['svmPredFileName'],
                rnn=survey['rnnPredFileName']
            )
            result_by_percentage = predictor.process_prediction_result(result_data)
            parsed_date = datetime.strptime(str(survey['created_at']), '%Y-%m-%d %H:%M:%S.%f%z')
            formatted_date = parsed_date.strftime('%Y-%m-%d %H:%M:%S')
            graphic_generator = GraphicGenerator()
            bacteria_graphics = graphic_generator.get_predicted_graphic(
                [item['bacteria'] for item in result_by_percentage], 
                survey['surveyFileName']
            )
            encoded_logo_img = encode_image_to_base64('images/brand-logo.png')

            context = {
                'created_at': formatted_date,
                'logo_img_data': encoded_logo_img,
                'number': survey['surveyNumber'],
                'result_data': result_by_percentage,
                'bacteria_images': bacteria_graphics,
                'BASE_URL': os.environ.get('BASE_URL', 'http://127.0.0.1:8000')
            }
            return render(request, 'pages/survey-result-pdf.html', context)
        
        else:
            messages.error(request, 'Error: Something went wrong!')
            return Http404("Survey not provided")
      
    except Exception as e:
        logger.error(e)
        messages.error(request, 'Error: Something went wrong!')
        return render(request, 'pages/survey-result-pdf.html')
    
def search_survey(request):
    form = SurveySearchForm()
    try:
        if request.method == 'POST':
            form = SurveySearchForm(request.POST)
            if form.is_valid():
                phone_no = form.cleaned_data['phone_no']
                reg_no = form.cleaned_data['reg_no']
                user_hash = hash_user(reg_no, phone_no)
                surveys = filter_survey_by_hash(user_hash)
                if len(surveys) > 0:
                    return render(request, 'pages/search_survey.html', {'form': form, 'surveys': surveys})
                else:
                    messages.error(request, 'Error: Survey not found', {'form': form})
                    return render(request, 'pages/search_survey.html')
            else:
                for field, errors in form.errors.items():
                    messages.error(request, errors)
                    return render(request, 'pages/search_survey.html',  {'form': form})
        else:
            return render(request, 'pages/search_survey.html', {'form': form})
    except Exception as e:
        logger.error(e)
        messages.error(request, 'Error: Something went wrong!')
        return render(request, 'pages/search_survey.html', {'form': form if form else SurveySearchForm()})
    
def test_load_model(request):
    index = request.GET.get('index')
    context = {'index': index}
    return render(request, 'pages/survey.html', context)

def test_sample_result(request, index):
    try:
        bacteria = STRAINS[index]
        test_data_reader = TestDataReader()
        x_data = test_data_reader.get_test_x_data_file(index)
        x_data_io = StringIO(x_data)
        x_data_array = np.genfromtxt(x_data_io, delimiter=',', skip_header=1)

        y_data = Bacteria.objects.get(label=bacteria)
        spectrum_list  = json.loads(y_data.spectrum)
        true_x_data_arr = np.array(spectrum_list)
        grapic_generator = GraphicGenerator()
        graphic_img_data = grapic_generator.create_graphic(title=bacteria, true_x_data=true_x_data_arr, x_data=x_data_array)
        res = json.dumps({
            'graphic_img_data': graphic_img_data
        })
        return HttpResponse(res, content_type="application/json")

    except Exception as e:
        logger.error(e)
        messages.error(request, 'Error: Something went wrong!')
        return render(request, 'pages/surveys.html')
    
def test_sample(request):
    index = request.GET.get('index')
    grapic_generator = GraphicGenerator()

    try:
        bacterias = [STRAINS[key] for key in STRAINS]
        bacteria = bacterias[int(index)]
        y_data = Bacteria.objects.get(label=bacteria)
        spectrum_list  = json.loads(y_data.spectrum)
        graphic_img_data = grapic_generator.create_graphic(title=bacteria, true_x_data=np.array(spectrum_list))
        res = json.dumps({
            'graphic_img_data': graphic_img_data
        })
        return HttpResponse(res, content_type="application/json")
    except Exception as e:
        logger.error(e)
        messages.error(request, 'Error: Something went wrong!')
        return render(request, 'pages/survey.html')

def test_survey_result(request, index):
    try:
        test_data_reader = TestDataReader()
        predictor = Predictor()
        data = test_data_reader.get_test_file(index)
        result_data = predictor.test_process_result_data(data)
        strains=[STRAINS[key] for key in STRAINS]
        indices = [strains.index(strain) for strain in result_data.keys() if strain in strains]
        filtered_colors = [COLORS[index] for index in indices]
        context = {
            'result_data': result_data,
            'colors': filtered_colors,
            'index': index
        }
        return render(request, 'pages/survey.html', context)
       
    except Exception as e:
        logger.error(e)
        messages.error(request, 'Error: Something went wrong!')
    return render(request, 'pages/survey.html')


def download_test_survey(request):
    result = request.GET.get('result')
    test_data_reader = TestDataReader()

    def get_predicted_graphic(df, surveyFileName):
        graphics = []
        grapic_generator = GraphicGenerator()

        x_data = test_data_reader.get_test_x_data_file(surveyFileName)
        for predicted_bacteria in df['Bacteria']:
            y_data = Bacteria.objects.get(label=predicted_bacteria)
            spectrum_list  = json.loads(y_data.spectrum)
            true_x_data_arr = np.array(spectrum_list)
            x_data_io = StringIO(x_data)
            x_data_array = np.genfromtxt(x_data_io, delimiter=',', skip_header=1)
            bacteria_img = {
                'bacteria': predicted_bacteria,
                'img_data':  grapic_generator.create_graphic(title=predicted_bacteria, true_x_data=true_x_data_arr, x_data=x_data_array)
            }
            graphics.append(bacteria_img)
        return graphics

    try:
        predictor = Predictor()

        data = test_data_reader.get_test_file(result)
        result_data = predictor.process_prediction_result(data.values)
        df = pd.DataFrame(list(result_data.items()), columns=['Bacteria', 'Percentage'])
        three_seconds_earlier = datetime.now() - timedelta(seconds=3)
        formatted_date = three_seconds_earlier.strftime('%Y-%m-%d %H:%M:%S')

        number = 'Тест-Шинжилгээний-Хариу' + result

        context = {
            'created_at': formatted_date,
            'logo_img_data': encode_image_to_base64('images/brand-logo.png'),
            'number': number,
            'result_data': result_data,
            'bacteria_images': get_predicted_graphic(df,result),
            'BASE_URL': os.environ.get('BASE_URL', 'http://127.0.0.1:8000')
        }
        resp_data = rendered_html('pages/survey-result-pdf.html', context)
        res = json.dumps({
            'resp_data': resp_data, 'survey_number': number
        })
        return HttpResponse(res, content_type="application/json")
      
    except Exception as e:
        logger.error(e)
        messages.error(request, 'Error: Something went wrong!')
        return render(request, 'pages/surveys.html')

def train_model(request):
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
            return HttpResponse('No trainable data returing')
        else:
            file_names = [data.file_name for data in not_trained_data]
            
            gpu_load_endpoint = GPU_SERVER_URL + 'model/train/'
            response = requests.post(gpu_load_endpoint, json={"file_names": file_names})
            if response.status_code == 200:
                data = response.json()
                trained_files = data['trained_files']
                for file_name in trained_files:
                    now = timezone.now()
                    TrainingData.objects.filter(file_name=file_name).update(status='trained', trained_at=now)
                print(f"---------------------------- {len(trained_files)} data trained ---------------------------- \n")
                return HttpResponse(f"---------------------------- {len(trained_files)} data trained ---------------------------- ")
            else:
                print(f"Failed to send data. Status code: {response.status_code}")
                return HttpResponse(f"Failed to send data. Status code: {response.status_code}")
    except Exception as e:
        logger.error(e)
        print('Error: ', e)
        return HttpResponse(e)
