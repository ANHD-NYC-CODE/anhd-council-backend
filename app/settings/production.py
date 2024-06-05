from app.settings.base import *

DEBUG = False
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = os.environ.get("EMAIL_USER", '')
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_PASSWORD", '')
EMAIL_PORT = 465
EMAIL_USE_TLS = True

ADMINS = (
    # ('Anhd admin', 'dapadmin@anhd.org'),
    ('Dev', 'scott@blueprintinteractive.com')
)

# Only want rollbar firing in production

# ROLLBAR = {
#     'access_token': os.environ.get('ROLLBAR_API_KEY', ''),
#     'environment': 'production',
#     'branch': 'master',
#     'root': BASE_DIR,
# }
