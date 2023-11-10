from django.shortcuts import render
from bacteraify.core import model as core_model
from django.shortcuts import redirect

def index(request):
    return render(request, 'index.html')

def login(request):
    return render(request, 'login.html')

def survery(request):
    return render(request, 'survey.html')

def faq(request):
    return render(request, 'faq.html')

def upload_survery(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['survey-file']
        file_name = core_model.save_file(uploaded_file)
        if file_name:
            redirect_url = '/survey/load/?file_name={}'.format(file_name)
            return redirect(redirect_url)
        else: 
            return render(request, 'survey.html')
    else:
        return render(request, 'survey.html')

def load_model(request):
    file_name = request.GET.get('file_name')
    print(file_name)
    return render(request, 'survey.html')