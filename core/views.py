from django.shortcuts import render
from rest_framework import viewsets
from datasets.helpers.api_helpers import cache_me, ApplicationViewSet
from rest_framework.permissions import IsAuthenticated
from core import models as c
from core import serializers as serial
from rest_framework.response import Response


class DatasetViewSet(ApplicationViewSet, viewsets.ReadOnlyModelViewSet):
    queryset = c.Dataset.objects.prefetch_related('update_set').prefetch_related('datafile_set').all().order_by('pk')
    serializer_class = serial.DatasetSerializer
    lookup_field = "model_name"

    @cache_me()
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_me()
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
