"""
Django settings for indavant project.

Generated by 'django-admin startproject' using Django 1.8.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


MAIN_URL = "http://127.0.0.1:8004/"


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'rbktijp2tx(1e_#)7s99w=@y6xj&&3xj8ev5b9yuxd%at%+y14'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'loginsys',
    'news',
    'userprofile',
    "favourite",
    "notify",
    "search",
    "ckeditor",
    "endless_pagination",
)


CKEDITOR_JQUERY_URL = '//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js'
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',

    }
}

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.core.files.uploadhandler.MemoryFileUploadHandler',
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',

)

ROOT_URLCONF = 'indavant.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'),  # Main templates
                 os.path.join(BASE_DIR, 'loginsys/templates'),  # Login system templates
                 os.path.join(BASE_DIR, 'news/templates'),  # News templates
                 os.path.join(BASE_DIR, 'news/templatetags'),
                 os.path.join(BASE_DIR, 'userprofile/templates'),  # User profile's templates
                 os.path.join(BASE_DIR, 'favourite/templates'),  # User favourite news templates
                 os.path.join(BASE_DIR, 'notify/templates'),  # User favourite news templates
                 os.path.join(BASE_DIR, 'search/templates'),  # User favourite news templates
                 ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.csrf',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS
TEMPLATE_CONTEXT_PROCESSORS += ('django.core.context_processors.request',)

WSGI_APPLICATION = 'indavant.wsgi.application'


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/django_cache',
        'TIMEOUT': 600,
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'ru-RU'
LANGUAGES = (
    ('ru', 'Russian'),
    ('en', 'English'),
)

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    ("static", os.path.join(BASE_DIR, 'static')),
)


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


import json
with open(BASE_DIR+"/indavant/admin_data_mail.json") as json_file:
#with open(BASE_DIR+"indavant/admin_data_mail.json") as json_file:
    json_data = json.load(json_file)


# E-mail
EMAIL_USE_SSL = True
EMAIL_HOST = json_data["host"]
EMAIL_PORT = json_data["port"]
EMAIL_HOST_USER = json_data["email"]
EMAIL_HOST_PASSWORD = json_data["password"]
DEFAULT_FROM_EMAIL = json_data["email"]
DEFAULT_TO_EMAIL = DEFAULT_FROM_EMAIL


