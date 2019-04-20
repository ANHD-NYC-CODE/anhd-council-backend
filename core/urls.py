from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import routers
from core import views as v
from rest_framework import mixins

router = routers.DefaultRouter()

router.register(r'datasets', v.DatasetViewSet)
router.register(r'bug-reports', v.BugReportViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
