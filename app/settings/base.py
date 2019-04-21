"""
Django settings for app project.

Generated by 'django-admin startproject' using Django 2.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""


import os
from kombu import Exchange, Queue
from datetime import timedelta
import sys
import datetime

TESTING = sys.argv[1:2] == ['test']

BATCH_SIZE = 100000
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY', '')
DEFAULT_ANNOTATION_DATE = datetime.datetime(  # jan 1st, last year
    year=datetime.datetime.now().year - 1, month=1, day=1).strftime('%Y-%m-%d')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', '%h(!920-v_1e6)%+@)$l9t5955a4m9v&_ipgawllvk-^_$2%=0')


# SECURITY WARNING: don't run with debug turned on in production!

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_results',
    'django_celery_beat',
    'django.contrib.postgres',
    'debug_toolbar',
    'django_filters',
    'rest_framework',
    'rest_framework_filters',
    'core',
    'datasets',
    'users.apps.UsersConfig',
    'rest_framework_simplejwt.token_blacklist'
]

AUTH_USER_MODEL = 'users.CustomUser'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS = [
    '127.0.0.1'
]

CORS_ORIGIN_ALLOW_ALL = False

CORS_ORIGIN_WHITELIST = (
    "localhost:3000",
    "portal.displacementalert.org"
)

ROOT_URLCONF = 'app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'anhd',
        'HOST':  os.environ.get('DATABASE_HOST', 'localhost'),
        'USER': 'anhd',
        'PORT':  os.environ.get('DATABASE_PORT', 5678)
    }
}

CACHES = {
    "default": {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://localhost:6378'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        "KEY_PREFIX": "DAP"
    }
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(hours=10),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,

}


REST_FRAMEWORK = {
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework_filters.backends.RestFrameworkFilterBackend',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    # 'DEFAULT_PAGINATION_CLASS': 'apps.core.pagination.StandardResultsSetPagination'
    # 'DEFAULT_RENDERER_CLASSES': (
    #     'rest_framework_csv.renderers.CSVRenderer',
    # ),
}


WSGI_APPLICATION = 'app.wsgi.application'
CACHE_TTL = 60 * 60 * 12  # cache for 12 hours
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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

EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = os.environ.get("EMAIL_USER", '')
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_PASSWORD", '')
EMAIL_PORT = 465
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'ANHD Team <noreply@anhd.org>'
EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY", '')

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'


USE_I18N = True

USE_L10N = True

USE_TZ = True
TIME_ZONE = "America/New_York"
# https://github.com/celery/django-celery-beat/issues/95
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = False
DJANGO_CELERY_BEAT_TZ_AWARE = True  # potential fix for beat spamming tasks?
CELERYBEAT_SCHEDULER = 'django_celery_beat.schedulers.DatabaseScheduler'

# https://stackoverflow.com/questions/19853378/how-to-keep-multiple-independent-celery-queues
# https://stackoverflow.com/questions/23129967/django-celery-multiple-queues-on-localhost-routing-not-working
# celery queues setup
CELERY_DEFAULT_QUEUE = 'celery'
CELERY_DEFAULT_EXCHANGE_TYPE = 'celery'
CELERY_DEFAULT_ROUTING_KEY = 'celery'
CELERY_QUEUES = (
    Queue('celery', Exchange('celery'), routing_key='celery'),
    Queue('update', Exchange('updates'), routing_key='updates'),
)

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
#
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATIC_URL = '/static/'
# STATICFILES_DIRS = (
#     os.path.join(BASE_DIR, 'static'),
# )

MEDIA_URL = '/data/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'data')
MEDIA_TEMP_ROOT = os.path.join(MEDIA_ROOT, 'temp')
LOG_ROOT = os.path.join(BASE_DIR, 'logs')

FLOWER_URL = "localhost:8888"
CELERY_BROKER_URL = os.environ.get('REDIS_URL', "redis://localhost:6378")
CELERY_RESULT_BACKEND = 'django-db'
CELERY_BACKEND = 'rpc://'
# Sensible settings for celery
CELERY_ALWAYS_EAGER = False
CELERY_ACKS_LATE = False
CELERY_TASK_PUBLISH_RETRY = True
CELERY_DISABLE_RATE_LIMITS = False
CELERY_BROKER_TRANSPORT_OPTIONS = {
    'visibility_timeout': 36000  # 10 hours
}
DJANGO_LOG_LEVEL = "DEBUG"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',

        }
    },
    'formatters': {
        'standard': {
            '()': 'colorlog.ColoredFormatter',
            'format': "%(log_color)s[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S",
            'log_colors': {
                'DEBUG':    'purple',
                'INFO':     'cyan',
                'WARNING':  'yellow',
                'ERROR':    'red',
                'CRITICAL': 'bold_red',
            },
        },
        'sql': {
            '()': 'colorlog.ColoredFormatter',
            'format': "%(log_color)s[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S",
            'log_colors': {
                'DEBUG':    'bold_green',
                'INFO':     'bold_blue',
                'WARNING':  'bold_yellow',
                'ERROR':    'bold_red',
                'CRITICAL': 'bold_red',
            },
        },
    },
    'handlers': {
        'logfile': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_ROOT, "dap-council.log"),
            'maxBytes': 1024 * 1024 * 5,  # 10MB
            'backupCount': 10,
            'formatter': 'standard',
        },
        'errorfile': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_ROOT, "dap-council.error.log"),
            'maxBytes': 1024 * 1024 * 5,  # 10MB
            'backupCount': 10,
            'formatter': 'standard',
        },
        'sql': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'sql',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'filters': ['require_debug_false']
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['sql'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.template': {
            'handlers': ['logfile'],
            'level': 'INFO',
            'propagate': False,
        },
        'app': {
            'handlers': ['console', 'sql', 'logfile', 'errorfile'],
            'level': 'DEBUG',
        },
    }
}

# Use exact model names from datasets/models
ACTIVE_MODELS = [
    'Council',
    'Community,'
    'Property',
    'Building',
    'TaxLot'
    'AddressRecord',
    'AcrisRealLegal',
    'AcrisRealMaster',
    'AcrisRealParty',
    'CoreSubsidyRecord',
    'DOBComplaint',
    'DOBNowFiledPermit',
    'DOBLegacyFiledPermit',
    'DOBPermitIssuedLegacy',
    'DOBPermitIssuedNow',
    'DOBFiledPermit',
    'DOBIssuedPermit',
    'DOBViolation',
    'ECBViolation',
    'Eviction',
    'HousingLitigation',
    'HPDBuildingRecord',
    'HPDComplaint',
    'HPDProblem',
    'HPDContact',
    'HPDRegistration',
    'HPDViolation',
    'RentStabilizationRecord',
    'SubsidyJ51',
    'Subsidy421a',
    'PublicHousingRecord',
    'TaxLien',
    'LisPenden',
    'LisPendenComment',
    'CONHRecord'

]
