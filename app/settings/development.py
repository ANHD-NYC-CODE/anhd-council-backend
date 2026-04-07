from app.settings.base import *
DEBUG = True


ADMINS = (
    # ('Dev', 'anhd.tech@gmail.com'),
    # ('Jack T. (Conceptual)', 'jack@conceptu.al'),
    # add yours here too!
)

CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True

# Override CSRF settings for localhost
CSRF_COOKIE_DOMAIN = None
CSRF_COOKIE_SECURE = False
CSRF_TRUSTED_ORIGINS = ['http://localhost:8000', 'http://localhost:3000']

# Dummy cache for dev use
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.dummy.DummyCache'
#     }
# }
