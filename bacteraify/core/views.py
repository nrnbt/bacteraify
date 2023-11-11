from django.shortcuts import render
from bacteraify.core import model as core_model
from django.shortcuts import redirect
import plotly.express as px
import plotly.offline as po

def index(request):
    return render(request, 'pages/index.html')

def login(request):
    return render(request, 'pages/login.html')

def survery(request):
    return render(request, 'pages/survey.html')

def faq(request):
    return render(request, 'pages/faq.html')

def upload_survery(request):
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

def load_model(request):
    file_name = request.GET.get('file_name')
    data = core_model.get_file(file_name, 'survey-files')
    core_model.predict(data)
    return render(request, 'pages/survey.html')

def survey_result(request):
    file_name = request.GET.get('file_name')
    data = core_model.get_file(file_name, 'survey-results')
    fig = px.line(data)
    plot_html = po.plot(fig, output_type='div')
    return render(request, 'pages/survey.html', {'plot_html': plot_html} )