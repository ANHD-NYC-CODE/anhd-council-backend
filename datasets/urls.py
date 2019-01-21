from django.urls import path
from datasets import views

urlpatterns = [
    path('councils/', views.council_list),
    path('councils/<int:pk>/', views.council_detail),
]
