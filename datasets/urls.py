from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from datasets import views

council_list = views.CouncilViewSet.as_view({
    'get': 'list',
})
council_detail = views.CouncilViewSet.as_view({
    'get': 'retrieve',
})
council_properties = views.CouncilViewSet.as_view({
    'get': 'properties',
})


urlpatterns = format_suffix_patterns([
    path('councils/', council_list, name='council-list'),
    path('councils/<int:pk>/', council_detail, name='council-detail'),
    path('councils/<int:pk>/properties/', council_properties, name='council-properties'),
    path('properties/<str:pk>/', views.PropertyDetail.as_view()),
])
