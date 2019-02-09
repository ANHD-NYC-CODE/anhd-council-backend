from app.settings.base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'anhd',
        'HOST': 'localhost',
        'USER': 'anhd',
        'PORT': '5432'
    }
}
