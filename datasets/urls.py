from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from datasets import views

urlpatterns = [
    path('councils/', views.CouncilList.as_view()),
    path('councils/<int:pk>/', views.CouncilDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
