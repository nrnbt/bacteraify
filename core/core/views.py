from django.shortcuts import render
from core.core import utils
from django.shortcuts import redirect
import plotly.express as px
import plotly.offline as po
import os
from django.contrib import messages
from bacter_identification.models import Survey
import logging
from django.http import HttpResponse, Http404
import pandas as pd
from io import StringIO
from core.core.utils import colors, hash_user, survey_result_available
from core.forms import SurveyForm, SurveySearchForm
from django.http import JsonResponse

logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'pages/index.html')

def survey(request):
    return render(request, 'pages/survey.html')

def faq(request):
    return render(request, 'pages/faq.html')

def upload_survey(request):
    try:
        if request.method == 'POST':
            form = SurveyForm(request.POST, request.FILES)
            if form.is_valid():
                phone_no = form.cleaned_data['phone_no']
                reg_no = form.cleaned_data['reg_no']
                file = form.cleaned_data['file']

                file_name = utils.save_file(file, 'survey-files')
                data = utils.get_file(file_name, 'survey-files')
                
                if file_name:
                    utils.save_survey(
                        user_id=request.user.id, 
                        user_email= request.user.email,
                        file_name=file_name, 
                        data_len=len(data),
                        userHash=hash_user(reg_no, phone_no)
                    )

                    return redirect('/survey/load/?file_name={}'.format(file_name))
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
        file_name = request.GET.get('file_name')
        if survey_result_available(file_name):
            return render(request, 'pages/survey.html', { 'survey_file_name': file_name })
        else:
            data = utils.get_file(file_name, 'survey-files')
            utils.predict(data, survey_file_name=file_name)
            return render(request, 'pages/survey.html', { 'survey_file_name': file_name })
       
    except Exception as e:
        logger.error(e)
        messages.error(request, 'Error: Something went wrong!')
    return render(request, 'pages/survey.html')

def survey_result(request):
    try:
        file_name = request.GET.get('file_name')
        data = utils.get_file(file_name, 'survey-results')
        result_data = utils.process_result_data(data.values)
        
        fig = px.line(data)
        plot_html = po.plot(fig, output_type='div')

        context = {
            'plot_html': plot_html,
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

    def get_file_contents(fileName, dir):
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), dir, fileName + '.csv')
        with open(file_path, 'rb') as file:
            return file.read()

    def send_file(file_contents, file_name):
        response = HttpResponse(file_contents, content_type='application/force-download')
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response
    
    try:
        if result is not None:
            data = utils.get_file(result, 'survey-results')
            result_data = utils.process_result_data(data.values)
            df = pd.DataFrame(list(result_data.items()), columns=['Bacteria', 'Percentage'])
            output = StringIO()
            df.to_csv(output, index=False)
            csv_string = output.getvalue()
            return send_file(csv_string, result + '.csv')
        
        elif survey is not None:
            file_contents = get_file_contents(survey, 'survey-files')
            return send_file(file_contents, survey + '.csv')
        
        else:
            messages.error(request, 'Error: Something went wrong!')
            return Http404("Filename not provided")
      
    except Exception as e:
        logger.error(e)
        messages.error(request, 'Error: Something went wrong!')
        return render(request, 'pages/surveys.html')

def check_survey_result(request, file_name=None):
    if file_name is not None:
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
                surveys = utils.filter_survey_by_hash(user_hash)
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