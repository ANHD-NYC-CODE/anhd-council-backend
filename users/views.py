from django.shortcuts import render
from rest_framework import viewsets
from datasets.helpers.api_helpers import ApplicationViewSet
from rest_framework.permissions import IsAuthenticated
from users import models as u
from users import serializers as serial
from rest_framework.response import Response


class UserViewSet(ApplicationViewSet, viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = u.CustomUser.objects.all()
    pagination_class = None

    def get_current_user(self, request, *args, **kwargs):
        serializer = serial.UserSerializer(request.user)
        return Response(serializer.data)
