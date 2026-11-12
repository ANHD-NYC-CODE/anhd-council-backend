from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import routers
from core import views as v
from core.views_health import celery_health_view
from rest_framework import mixins

router = routers.DefaultRouter()

router.register(r'datasets', v.DatasetViewSet)
router.register(r'user-messages', v.UserMessageViewSet)

urlpatterns = [
    path('health/celery/', celery_health_view, name='celery_health'),
    path('', include(router.urls)),
]
