"""
Django settings for bacteraify project.

Generated by 'django-admin startproject' using Django 4.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import os 
import logging
import dj_database_url

logger = logging.getLogger(__name__)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

def load_env_variables(env_file=".env"):
    try:
        with open(env_file) as file:
            for line in file:
                if line.startswith('#') or not line.strip():
                    continue
                key, value = line.strip().split('=', 1)
                os.environ[key] = value
    except Exception as e:
        logger.warning(e)

load_env_variables()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-%7j^iwbsz(l7#=job4a7oc*!4om8oj82^gr-_-#qz47t5p6kmy'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'authentication',
    'admin_soft.apps.AdminSoftDashboardConfig',
    # 'admin'
    'bacter_identification',
    'whitenoise.runserver_nostatic',
]

AUTH_USER_MODEL = 'authentication.UserAuth'
AUTHENTICATION_BACKENDS = ['authentication.backends.EmailBackend']

LOGIN_URL = '/login/'
BASE_URL = os.environ.get('BASE_URL', 'http://127.0.0.1:8000')
# ASGI_APPLICATION = 'core.asgi.application'

WEB_ENDPOINT = os.environ.get('WEB_ENDPOINT', '127.0.0.1')
# REDIS_CHANNEL_LAYER_PORT = os.environ.get('REDIS_CHANNEL_LAYER_PORT', '6379')
MY_SQL_PORT = os.environ.get('MY_SQL_PORT', '3306')
MY_SQL_DB = os.environ.get('MY_SQL_DB', 'bacteraify')
MY_SQL_USER = os.environ.get('MY_SQL_USER', '')
MY_SQL_PASS = os.environ.get('MY_SQL_PASS', '')
MY_SQL_HOST= os.environ.get('MY_SQL_HOST', '')
# CHANNEL_LAYERS = {
#     'default': {
#         'BACKEND': 'channels_redis.core.RedisChannelLayer',
#         'CONFIG': {
#             "hosts": [(WEB_ENDPOINT, REDIS_CHANNEL_LAYER_PORT)],
#         },
#     },
# }

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.your-email-provider.com')
EMAIL_PORT = os.environ.get('EMAIL_PORT', 587)
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', True)
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'example@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'pass')

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR/'core'/'templates', BASE_DIR/'admin'/'admin-templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': MY_SQL_DB,
        'USER': MY_SQL_USER,
        'PASSWORD': MY_SQL_PASS,
        'HOST': MY_SQL_HOST,
        'PORT': MY_SQL_PORT
    }
}

# DATABASES['default'] = dj_database_url.config(conn_max_age=600, ssl_require=True)
# DATABASES['default']['OPTIONS']['charset'] = 'utf8mb4'
# del DATABASES['default']['OPTIONS']['sslmode']
# DATABASES['default']['OPTIONS']['ssl'] =  {'ca': os.environ.get('MYSQL_ATTR_SSL_CA')}

# if 'OPTIONS' not in DATABASES['default']:
#     DATABASES['default']['OPTIONS'] = {}

# DATABASES['default']['OPTIONS']['charset'] = 'utf8mb4'

# if 'sslmode' in DATABASES['default']['OPTIONS']:
#     del DATABASES['default']['OPTIONS']['sslmode']

# DATABASES['default']['OPTIONS']['ssl'] = {'ca': os.environ.get('MYSQL_ATTR_SSL_CA')}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Singapore'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATICFILES_DIRS = [
    BASE_DIR / "core" / "static",
    BASE_DIR / "admin" / "static"
]

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "core" / "staticfiles"
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "core" / "media"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
