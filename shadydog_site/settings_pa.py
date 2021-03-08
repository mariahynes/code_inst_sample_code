from .settings import *

import os

DEBUG = False

ALLOWED_HOSTS = [
    '127.0.0.1',
    'shadydog.eu.pythonanywhere.com',
    'shadydogdesign.com',
    'www.shadydogdesign.com',
]

DOMAIN_URL ='https://www.shadydogdesign.com/'
SITE_ORDER_URL = DOMAIN_URL + "admin/orders/order/"

SECRET_KEY = os.getenv('SECRET_KEY')
CSRF_COOKIE_SECURE = True


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Add whitenoise middleware after the security middleware                             
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
WHITENOISE_MANIFEST_STRICT = False

STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'  
#STATIC_ROOT = os.path.join(BASE_DIR,'static')
STATIC_ROOT = BASE_DIR / 'static'
STATIC_URL = '/static/'

SITE_DISPLAY_NAME = "Shady Dog"

EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

DEFAULT_FILE_STORAGE = 'storages.backends.azure_storage.AzureStorage'
AZURE_ACCOUNT_NAME = os.getenv('AZURE_ACCOUNT_NAME')
AZURE_ACCOUNT_KEY = os.getenv('AZURE_ACCOUNT_KEY')
AZURE_CONTAINER = os.getenv('AZURE_CONTAINER')

MEDIA_URL = os.getenv('MEDIA_URL')