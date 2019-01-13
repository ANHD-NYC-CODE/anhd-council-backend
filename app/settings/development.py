from app.settings.base import *

FLOWER_URL = "localhost:8888"
CELERY_BROKER_URL = 'redis://localhost:6378'
DEBUG = True


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'anhd',
        'HOST': 'localhost',
        'USER': 'anhd',
        'PORT': '5678'
    }
}
