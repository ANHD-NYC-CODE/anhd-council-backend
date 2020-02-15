from django.shortcuts import render
from rest_framework import viewsets
from datasets.helpers.cache_helpers import cache_request_path
from datasets.helpers.api_helpers import ApplicationViewSet
from rest_framework.permissions import IsAuthenticated
from core import models as c
from core import serializers as serial
from rest_framework.response import Response
from rest_framework import mixins


class DatasetViewSet(ApplicationViewSet, viewsets.ReadOnlyModelViewSet):
    queryset = c.Dataset.objects.prefetch_related(
        'update_set').prefetch_related('datafile_set').all()
    serializer_class = serial.DatasetSerializer
    lookup_field = "model_name"

    @cache_request_path()
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_request_path()
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class UserMessageViewSet(ApplicationViewSet, mixins.CreateModelMixin,
                         viewsets.GenericViewSet):
    queryset = c.UserMessage.objects.all()
    serializer_class = serial.UserMessageSerializer
