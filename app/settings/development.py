from app.settings.base import *

DEBUG = True

EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = os.environ.get("EMAIL_USER", '')
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_PASSWORD", '')
EMAIL_PORT = 465
EMAIL_USE_TLS = True

ADMINS = (
    ('Dev', 'anhd.tech@gmail.com'),
)
