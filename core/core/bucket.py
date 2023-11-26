# In your views.py or another relevant file

from .s3_utils import download_model_from_s3

def some_view(request):
    download_model_from_s3('bacteraify-model', 's3://bacteraify-model/cnn_model.h5', '../core/models/cnn_model.h5')