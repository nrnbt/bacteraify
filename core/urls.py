"""
URL configuration for bacteraify project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from core.core import views as core_views
import authentication.views as auth_views
import admin.views as admin_views

urlpatterns = [
    path('', core_views.index, name='home'),
    path('login/', auth_views.user_login, name='login'),
    path('logout/', auth_views.user_logout, name='logout'),
    # path('login/', auth_views.user_login, name='login'),
    path('survey/', core_views.survey, name='survey'),
    path('survey/upload/', core_views.upload_survey, name='upload-survey'),
    path('survey/load/', core_views.load_model, name='load-model'),
    path('survey/result/', core_views.survey_result, name='survey-result'),
    path('faq/', core_views.faq, name='faq'),
]

admin.site.get_urls = lambda: [
    path('my_custom_view/', admin_views)
] + admin.site.get_urls()


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
