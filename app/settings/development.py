from app.settings.base import *

FLOWER_URL = "localhost:8888"
CELERY_BROKER_URL = 'redis://localhost:6378'
DEBUG = True

EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = os.environ.get("EMAIL_USER", '')
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_PASSWORD", '')
EMAIL_PORT = 465
EMAIL_USE_TLS = True

ADMINS = (
    ('Dev', 'xxstarcat@gmail.com'),
)

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
