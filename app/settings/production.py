from app.settings.base import *

FLOWER_URL = "localhost:8888"
CELERY_BROKER_URL = 'redis://redis'
DEBUG = False


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'anhd',
        'HOST': 'postgres',
        'USER': 'anhd',
        'PORT': '5432'
    }
}
