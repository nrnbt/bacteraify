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

from main.core import views as core_views
import authentication.views as auth_views
import admin.views as admin_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as admin_auth_views

urlpatterns = [
    path('', core_views.index, name='home'),
    path('faq/', core_views.faq, name='faq'),

    path('login/', auth_views.merch_emp_login, name='login'),
    path('logout/', auth_views.user_logout, name='logout'),
    path('reset-pass/', auth_views.reset_pass, name='reset-pass'),
    path('set-password/<uidb64>/<token>/<email>/<type>', auth_views.password_reset_confirm, name='set-password'),

    path('merch-login/', auth_views.merch_admin_login, name='merch-login'),
    path('merch/', login_required(auth_views.merch_home), name='merch-home'),
    path('merch-dashboard/', login_required(auth_views.merch_dashboard), name='merch-dashboard'),
    path('merch-employee/', login_required(auth_views.merch_employee), name='merch-employee'),
    path('merch-employee/register', login_required(auth_views.employee_register), name='register-employee'),
    
    path('survey/', core_views.survey, name='survey'),
    path('survey/upload/', login_required(core_views.upload_survey), name='upload-survey'),
    path('survey/load/', login_required(core_views.load_model), name='load-model'),
    path('survey/check-result/<id>/', login_required(core_views.check_survey_result), name = "check-survey-result"),
    path('survey/result/', login_required(core_views.survey_result), name='survey-result'),
    path('survey/result-pdf/', login_required(core_views.survey_result_pdf_view), name='survey-result-pdf'),

    path('surveys/', login_required(core_views.surveys), name='surveys'),
    path('search-survey/', login_required(core_views.search_survey), name='search-survey'),
    path('download-result/', login_required(core_views.download_survey), name='download-survey'),

    path('test/samples/', core_views.test_sample, name='test-sample'),
    path('test/survey/load/', core_views.test_load_model, name='test-load-model'),
    path('test/survey/result/<str:index>', core_views.test_survey_result, name='test-survey-result'),
    path('test/download/', core_views.download_test_survey, name='download-test-survey'),

    path('admin/', admin_views.index, name='admin-index'),
    path('admin/login/', admin_views.admin_login, name='admin-login'),
    path('admin/logout/', admin_views.admin_logout, name='admin-logout'),
    path('admin/password-change/', admin_views.UserPasswordChangeView.as_view(), name='password_change'),
    path('admin/password-change/', admin_views.UserPasswordChangeView.as_view(), name='password_change'),
    path('admin/password-change-done/',admin_views.PasswordChangeDoneView, name="password_change_done"),
    path('admin/password-reset/', admin_views.UserPasswordResetView.as_view(), name='password_reset'),
    path('admin/password-reset-confirm/<uidb64>/<token>/', admin_views.UserPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('admin/password-reset-done/', admin_views.PasswordResetDoneView, name='password_reset_done'),
    path('accounts/password-reset-complete/', admin_views.PasswordResetCompleteView, name='password_reset_complete'),

    path('admin/dashboard/', admin_views.dashboard, name='admin-dashboard'),
    path('admin/merchant/<int:id>', admin_views.merchant, name='admin-merchant'),
    path('admin/merchants/', admin_views.merchants, name='admin-merchants'),
    path('admin/merchants/register/', admin_views.register_merchant, name='admin-register-merchant'),
    
    path('more/', core_views.more, name='more'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
