from app.settings.base import *

FLOWER_URL = "localhost:8888"
CELERY_BROKER_URL = 'redis://redis'
DEBUG = False

EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = os.environ.get("EMAIL_USER", '')
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_PASSWORD", '')
EMAIL_PORT = 465
EMAIL_USE_TLS = True

ADMINS = (
    ('Dev', 'anhd.tech@gmail.com'),
)

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'anhd',
        'HOST': os.environ.get('DATABASE', 'postgres'),
        'USER': 'anhd',
        'PORT': '5432'
    }
}

CACHES = {
    "default": {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        "KEY_PREFIX": "DAP"
    }
}
