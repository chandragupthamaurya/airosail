"""
Django settings for reposts project.

Generated by 'django-admin startproject' using Django 3.2.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
import os
from django.core.management.utils import get_random_secret_key
from urllib.parse import urlparse
from . import secret

Oauth = secret.Oauth_element()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = (Oauth.SECRET_KEY)


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = Oauth.DEBUG

ALLOWED_HOSTS = ["127.0.0.1","localhost","156.67.218.171","airosail.com","www.airosail.com"]

# Application definition

INSTALLED_APPS = [
    'feed',
    'users',
    'ckeditor',
    'taggit',
    'notifications',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'reposts.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templates')],
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

WSGI_APPLICATION = 'reposts.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

if os.getenv("DATABASES_URL","") != "":
    r.urlparse(os.environ.get("DATABASES_URL"))
    DATABASES = {
        "default":{
            'ENGINE':"django.db.backends.postgresql_psycopg2",
            "NAME":os.path.relpath(r.path,"/"),
            "USER": r.username,
            "PASSWORD":r.password,
            "HOST":r.hostname,
            "PORT":r.port,
            "OPTIONS":{"sslmode":"require"},

        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }



# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/


LOGIN_REDIRECT_URL = 'users:dashboard'
LOGIN_URL = 'feed:index'

STATIC_URL = '/static/'
if DEBUG:
    STATIC_ROOT = '/static/'
else:
    STATIC_ROOT = os.path.join(BASE_DIR,'staticfiles')
STATICFILES_DIRS = (os.path.join('static'),)

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

EMAIL_BACKEND = Oauth.EMAIL_BACKEND
EMAIL_HOST = Oauth.EMAIL_HOST
EMAIL_USE_TLS = Oauth.EMAIL_USE_TLS
EMAIL_PORT = Oauth.EMAIL_PORT
EMAIL_HOST_USER = Oauth.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = Oauth.EMAIL_HOST_PASSWORD

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# extra configs
CKEDITOR_CONFIGS = {
    'default': {
        'width': '100%',
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink'],
            ['RemoveFormat', 'Source']
        ]
    },
}
CKEDITOR_BASEPATH = os.path.join(BASE_DIR,"/static/ckeditor/ckeditor/")

DJANGO_NOTIFICATIONS_CONFIG = { 'USE_JSONFIELD': True}

