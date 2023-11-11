from django.shortcuts import render
from bacteraify.core import model as core_model
from django.shortcuts import redirect
import plotly.express as px
import plotly.offline as po
import os
from django.contrib import messages

def index(request):
    return render(request, 'pages/index.html')

def login(request):
    return render(request, 'pages/login.html')

def survey(request):
    return render(request, 'pages/survey.html')

def faq(request):
    return render(request, 'pages/faq.html')

def upload_survey(request):
    try:
        if request.method == 'POST':
            uploaded_file = request.FILES['survey-file']
            file_name = core_model.save_file(uploaded_file, 'survey-files')
            if file_name:
                redirect_url = '/survey/load/?file_name={}'.format(file_name)
                return redirect(redirect_url)
            else: 
                return render(request, 'pages/survey.html')
        else:
            return render(request, 'pages/survey.html')
    except Exception as e:
        messages.error(request, 'Error: Something went wrong!')
    return render(request, 'pages/survey.html')

def load_model(request):
    try:
        file_name = request.GET.get('file_name')
        data = core_model.get_file(file_name, 'survey-files')
        core_model.predict(data)

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
        fig = px.line(data)
        plot_html = po.plot(fig, output_type='div')

        context = {
            'plot_html': plot_html
        }

        return render(request, 'pages/survey.html', context)
    except Exception as e:
        messages.error(request, 'Error: Something went wrong!')
    return render(request, 'pages/survey.html')
