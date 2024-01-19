from django.shortcuts import render
from django.shortcuts import redirect
import os
from django.contrib import messages
from bacter_identification.models import Survey, Bacteria
import logging
from django.http import Http404, JsonResponse, HttpResponse
import pandas as pd
from io import StringIO
from core.core.utils import hash_user, save_file, get_file, predict, process_result_data, get_file_contents, diff_graphic, rendered_html, get_test_file, get_test_x_data_file, encode_image_to_base64, single_graphic
from core.core.survey import create_survey, survey_result_available, filter_survey_by_hash
from core.core.constants import colors, STRAINS
from core.forms import SurveyForm, SurveySearchForm
import json
import numpy as np
from datetime import datetime, timedelta
import ast

logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'pages/index.html')

def survey(request):
    context = {
        'strains': [STRAINS[key] for key in STRAINS]
    }
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

                file_name = save_file(file, 'survey-files')
                data = get_file(file_name, 'survey-files')
                
                if file_name:
                    survey_id = create_survey(
                        user_id=request.user.id, 
                        user_email= request.user.email,
                        file_name=file_name, 
                        data_len=len(data),
                        patient_hash=hash_user(reg_no, phone_no),
                        model_types = model_types
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
        def check_status(s):
            s = s.replace(" predicted", "")
            numbers = s.split("/")
            if len(numbers) == 2 and numbers[0].strip() == numbers[1].strip():
                return True
            else:
                return False
        survey_id = request.GET.get('id')
        survey = Survey.objects.filter(id=survey_id).values('surveyFileName', 'modelTypes', 'status').first()
        file_name = survey['surveyFileName']
        model_types = survey['modelTypes']
        status = survey['status']
        predicted = check_status(status)
        if predicted:
            return redirect('survey-result', { 'survey_file_name': file_name })
        else:
            data = get_file(file_name, 'survey-files')
            predict(data, survey_file_name=file_name, model_types=model_types)
            return render(request, 'pages/survey.html', { 'survey_file_name': file_name })
    except Survey.DoesNotExist:
        raise Http404("Survey does not exist")
    except Exception as e:
        logger.error(e)
        messages.error(request, 'Error: Something went wrong!')
    return render(request, 'pages/survey.html')

def survey_result(request):
    try:
        survey_id = request.GET.get('survey_id')
        survey = Survey.objects.filter(id=survey_id).values('surveyFileName', 'modelTypes', 'status', 'cnnPredFileName', 'svmPredFileName', 'rnnPredFileName').first()
        model_types = survey['modelTypes']
        data = {}
        model_types_list = ast.literal_eval(model_types)
        print(model_types_list)
        for char in model_types_list:
            if char == 'CNN':
                data[char] = get_file(survey['cnnPredFileName'], 'survey-results') 
            elif char == 'SVM':
                data[char] = get_file(survey['svmPredFileName'], 'survey-results') 
            elif char == 'RNN':
                data[char] = get_file(survey['rnnPredFileName'], 'survey-results')

        print('data', data)
        result_data = process_result_data(data.values)
        context = {
            'result_data': result_data,
            'colors': colors
        }

        return render(request, 'pages/survey.html', context)
    except Exception as e:
        logger.error(e)
        messages.error(request, 'Error: Something went wrong!')
    return render(request, 'pages/survey.html')

def surveys(request):
    try:
        surveys = Survey.objects.filter(userId=request.user.id)
        context = {
            'surveys': surveys
        }
    except Exception as e:
        logger.error(e)
        messages.error(request, 'Error: Something went wrong!')
    return render(request, 'pages/surveys.html', context)

def download_survey(request):
    survey = request.GET.get('survey')
    result = request.GET.get('result')

    def get_csv_file_contents(fileName, dir):
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), dir, fileName + '.csv')
        with open(file_path, 'rb') as file:
            return file.read()
        
    def send_csv(file_contents, file_name):
        response = HttpResponse(file_contents, content_type='application/force-download')
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response

    def get_predicted_graphic(df, surveyFileName):
        graphics = []

        x_data = get_file_contents(surveyFileName,'survey-files')
        for predicted_bacteria in df['Bacteria']:
            y_data = Bacteria.objects.get(label=predicted_bacteria)
            spectrum_list  = json.loads(y_data.spectrum)
            y_data_array = np.array(spectrum_list)

            x_data_io = StringIO(x_data)
            x_data_array = np.genfromtxt(x_data_io, delimiter=',', skip_header=1)
            bacteria_img = {
                'bacteria': predicted_bacteria,
                'img_data':  diff_graphic(predicted_bacteria, y_data_array, x_data_array)
            }
            graphics.append(bacteria_img)

        return graphics

    try:
        if result is not None:
            data = get_file(result, 'survey-results')
            result_data = process_result_data(data.values)
            df = pd.DataFrame(list(result_data.items()), columns=['Bacteria', 'Percentage'])

            survey = Survey.objects.get(resultFileName=result)
            parsed_date = datetime.strptime(str(survey.created_at), '%Y-%m-%d %H:%M:%S.%f%z')
            formatted_date = parsed_date.strftime('%Y-%m-%d %H:%M:%S')

            context = {
                'created_at': formatted_date,
                'logo_img_data': encode_image_to_base64('images/brand-logo.png'),
                'number': survey.number,
                'result_data': result_data,
                'bacteria_images': get_predicted_graphic(df,survey.surveyFileName),
                'BASE_URL': os.environ.get('BASE_URL', 'http://127.0.0.1:8000')
            }
            resp_data = rendered_html('pages/survey-result-pdf.html', context)
            res = json.dumps({
                'resp_data': resp_data, 'survey_number': survey.number 
            })
            return HttpResponse(res, content_type="application/json")
        
        elif survey is not None:
            file_contents = get_csv_file_contents(survey, 'survey-files')
            return send_csv(file_contents, survey + '.csv')
        
        else:
            messages.error(request, 'Error: Something went wrong!')
            return Http404("Filename not provided")
      
    except Exception as e:
        logger.error(e)
        messages.error(request, 'Error: Something went wrong!')
        return render(request, 'pages/surveys.html')

def check_survey_result(request, id=None):
    if id is not None:
        result = survey_result_available(file_name)
        if result is not None:
            return JsonResponse({"result_file_name": result})
        else:
            return JsonResponse({"error": 'result not found'})
    else:
        return JsonResponse({"error": 'survey not found'})
    
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
        x_data = get_test_x_data_file(index)
        x_data_io = StringIO(x_data)
        x_data_array = np.genfromtxt(x_data_io, delimiter=',', skip_header=1)

        y_data = Bacteria.objects.get(label=bacteria)
        spectrum_list  = json.loads(y_data.spectrum)
        y_data_array = np.array(spectrum_list)

        graphic_img_data = diff_graphic(bacteria, y_data_array, x_data_array)
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
    try:
        bacterias = [STRAINS[key] for key in STRAINS]
        bacteria = bacterias[int(index)]
        y_data = Bacteria.objects.get(label=bacteria)
        spectrum_list  = json.loads(y_data.spectrum)
        y_data_array = np.array(spectrum_list)
        graphic_img_data = single_graphic(bacteria, y_data_array)
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
        data = get_test_file(index)
        result_data = process_result_data(data.values)
        strains=[STRAINS[key] for key in STRAINS]
        indices = [strains.index(strain) for strain in result_data.keys() if strain in strains]
        filtered_colors = [colors[index] for index in indices]
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
    def get_predicted_graphic(df, surveyFileName):
        graphics = []

        x_data = get_test_x_data_file(surveyFileName)
        for predicted_bacteria in df['Bacteria']:
            y_data = Bacteria.objects.get(label=predicted_bacteria)
            spectrum_list  = json.loads(y_data.spectrum)
            y_data_array = np.array(spectrum_list)
            x_data_io = StringIO(x_data)
            x_data_array = np.genfromtxt(x_data_io, delimiter=',', skip_header=1)
            bacteria_img = {
                'bacteria': predicted_bacteria,
                'img_data':  diff_graphic(predicted_bacteria, y_data_array, x_data_array)
            }
            graphics.append(bacteria_img)
        return graphics

    try:
        data = get_test_file(result)
        result_data = process_result_data(data.values)
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
