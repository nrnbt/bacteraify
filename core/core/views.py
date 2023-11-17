from django.shortcuts import render
from core.core import survey as core_model
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
            uploaded_file = request.FILES['survey-file']
            file_name = core_model.save_file(uploaded_file, 'survey-files')
            data = core_model.get_file(file_name, 'survey-files')
            if file_name:

                core_model.save_record(user_id=request.user.id, user_email= request.user.email, file_name=file_name, data_len=len(data))

                redirect_url = '/survey/load/?file_name={}'.format(file_name)
                return redirect(redirect_url)
            else: 
                return render(request, 'pages/survey.html')
        else:
            return render(request, 'pages/survey.html')
    except Exception as e:
        logger.error(e)
        messages.error(request, 'Error: Something went wrong!')
    return render(request, 'pages/survey.html')

def load_model(request):
    try:
        file_name = request.GET.get('file_name')
        data = core_model.get_file(file_name, 'survey-files')
        core_model.predict(data, survey_file_name=file_name)

        context = {
            'SOCKET_PORT': os.environ.get('SOCKET_PORT', '8001'),
        }

        return render(request, 'pages/survey.html', context)
    except Exception as e:
        messages.error(request, 'Error: Something went wrong!')
    return render(request, 'pages/survey.html')

def survey_result(request):
    try:
        file_name = request.GET.get('file_name')
        data = core_model.get_file(file_name, 'survey-results')
        result_data = core_model.process_result_data(data.values)
        
        fig = px.line(data)
        plot_html = po.plot(fig, output_type='div')

        context = {
            'plot_html': plot_html,
            'result_data': result_data
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
            data = core_model.get_file(result, 'survey-results')
            result_data = core_model.process_result_data(data.values)
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
