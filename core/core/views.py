from django.shortcuts import render
from django.shortcuts import redirect
import os
from django.contrib import messages
from bacter_identification.models import Survey, Bacteria
import logging
from django.http import Http404, JsonResponse, HttpResponse
import pandas as pd
from io import StringIO
from core.core.utils import hash_user, FileWriter, FileReader, Predictor, TestDataReader, GraphicGenerator, rendered_html, encode_image_to_base64
from core.core.survey import create_survey, survey_result_available, filter_survey_by_hash
from core.core.constants import COLORS, STRAINS
from core.forms import SurveyForm, SurveySearchForm
import json
import numpy as np
from datetime import datetime, timedelta
from core.core.types import FileDir

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
                file_reader = FileReader()
                file_writer = FileWriter()

                file_name = file_writer.save_file(file, FileDir.SURVEY)
                data = file_reader.get_file_contents(file_name, FileDir.SURVEY)
                
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
        survey_id = request.GET.get('id')
        survey = Survey.objects.filter(id=survey_id).values('surveyFileName', 'modelTypes', 'status').first()
        predicted = survey_result_available(survey['status'])
        if predicted:
            return redirect('/survey/result/?id={}'.format(survey_id))
        else:
            file_name = survey['surveyFileName']
            model_types = survey['modelTypes']
            file_reader = FileReader()
            data = file_reader.get_file_contents(file_name, FileDir.SURVEY)
            predictor = Predictor()
            predictor.predict(data, survey_file_name=file_name, model_types=model_types)
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
        data = {}

        predictor = Predictor()
        result = predictor.process_prediction_result(
            model_types=model_types,
            cnn=survey['cnnPredFileName'],
            svm=survey['svmPredFileName'],
            rnn=survey['rnnPredFileName']
        )

        context = {
            'result_data': result,
            'colors': COLORS
        }

        return render(request, 'pages/survey.html', context)
    except Exception as e:
        logger.error(e)
        messages.error(request, 'Error: Something went wrong!')
    return render(request, 'pages/survey.html')

def surveys(request):
    try:
        surveys = Survey.objects.filter(userId=request.user.id)
        context = { 'surveys': surveys }
    except Exception as e:
        logger.error(e)
        messages.error(request, 'Error: Something went wrong!')
    return render(request, 'pages/surveys.html', context)

def download_survey(request):
    result = request.GET.get('result')
    survey = Survey.objects.filter(id=result).values('modelTypes', 'cnnPredFileName', 'svmPredFileName', 'rnnPredFileName', 'created_at', 'surveyNumber', 'surveyFileName').first()
    
    file_reader = FileReader()
    predictor = Predictor()

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
        graphic_generator = GraphicGenerator()

        x_data = file_reader.get_file(surveyFileName, FileDir.SURVEY)
        for predicted_bacteria in df['bacteria']:
            y_data = Bacteria.objects.get(label=predicted_bacteria)
            spectrum_list  = json.loads(y_data.spectrum)
            y_data_array = np.array(spectrum_list)

            x_data_io = StringIO(x_data)
            x_data_array = np.genfromtxt(x_data_io, delimiter=',', skip_header=1)
            bacteria_img = {
                'bacteria': predicted_bacteria,
                'img_data':  graphic_generator.create_graphic(title=predicted_bacteria, x_data=x_data_array, y_data=y_data_array)
            }
            graphics.append(bacteria_img)

        return graphics

    try:
        if result is not None:
            result_data = predictor.process_prediction_result(
                model_types=survey['modelTypes'],
                cnn=survey['cnnPredFileName'],
                svm=survey['svmPredFileName'],
                rnn=survey['rnnPredFileName']
            )
            
            parsed_date = datetime.strptime(str(survey['created_at']), '%Y-%m-%d %H:%M:%S.%f%z')
            formatted_date = parsed_date.strftime('%Y-%m-%d %H:%M:%S')

            context = {
                'created_at': formatted_date,
                'logo_img_data': encode_image_to_base64('images/brand-logo.png'),
                'number': survey['surveyNumber'],
                'result_data': result_data,
                'bacteria_images': get_predicted_graphic(pd.DataFrame(result_data),survey['surveyFileName']),
                'BASE_URL': os.environ.get('BASE_URL', 'http://127.0.0.1:8000')
            }
            resp_data = rendered_html('pages/survey-result-pdf.html', context)
            res = json.dumps({
                'resp_data': resp_data, 'survey_number': survey['surveyNumber']
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
        survey = Survey.objects.filter(id=id).values('status').first()
        predicted = survey_result_available(survey['status'])
        if predicted:
            return JsonResponse({"id": id})
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
        test_data_reader = TestDataReader()
        x_data = test_data_reader.get_test_x_data_file(index)
        x_data_io = StringIO(x_data)
        x_data_array = np.genfromtxt(x_data_io, delimiter=',', skip_header=1)

        y_data = Bacteria.objects.get(label=bacteria)
        spectrum_list  = json.loads(y_data.spectrum)
        y_data_array = np.array(spectrum_list)

        grapic_generator = GraphicGenerator()
        graphic_img_data = grapic_generator.create_graphic(title=bacteria, y_data=y_data_array, x_data=x_data_array)
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
        y_data_array = np.array(spectrum_list)
        graphic_img_data = grapic_generator.create_graphic(title=bacteria, y_data=y_data_array)
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
        result_data = predictor.process_prediction_result(data.values)
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
            y_data_array = np.array(spectrum_list)
            x_data_io = StringIO(x_data)
            x_data_array = np.genfromtxt(x_data_io, delimiter=',', skip_header=1)
            bacteria_img = {
                'bacteria': predicted_bacteria,
                'img_data':  grapic_generator.create_graphic(title=predicted_bacteria, y_data=y_data_array, x_data=x_data_array)
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
