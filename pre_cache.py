# Script run after deploy to pre cache all council + community property summaries in redis
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
import django
django.setup()

from core.utils.cache import create_async_cache_workers

create_async_cache_workers()
