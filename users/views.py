from django.shortcuts import render
from django.http import QueryDict
from rest_framework import viewsets
from datasets.helpers.api_helpers import ApplicationViewSet
from rest_framework.permissions import IsAuthenticated
from users import models as u
from users import serializers as serial
from rest_framework.response import Response
from rest_framework import generics, mixins, status


class UserViewSet(ApplicationViewSet, viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = u.CustomUser.objects.all()
    pagination_class = None

    def get_current_user(self, request, *args, **kwargs):
        serializer = serial.UserSerializer(request.user)
        return Response(serializer.data)


class UserRequestViewSet(ApplicationViewSet,
                         mixins.CreateModelMixin,
                         viewsets.GenericViewSet):
    queryset = u.UserRequest.objects.all()
    serializer_class = serial.UserRequestSerializer


class UserBookmarkedPropertiesCollection(mixins.ListModelMixin,
                                         mixins.CreateModelMixin,
                                         generics.GenericAPIView):

    queryset = u.UserBookmarkedProperties.objects.all()
    serializer_class = serial.UserBookmarkedPropertiesSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = request.user
        queryset = user.userbookmarkedproperties_set.all()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        data_dict = request.data.dict()
        mutable_query_dict = QueryDict(mutable=True)
        mutable_query_dict.update(data_dict)
        mutable_query_dict.__setitem__('user_id', request.user.id)

        serializer = self.get_serializer(data=mutable_query_dict)
        serializer.is_valid(raise_exception=True)
        serializer.create(validated_data=mutable_query_dict.dict())
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class UserBookmarkedPropertiesMember(mixins.DestroyModelMixin,
                                     generics.GenericAPIView):

    queryset = u.UserBookmarkedProperties.objects.all()
    serializer_class = serial.UserBookmarkedPropertiesSerializer
    permission_classes = (IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user == request.user:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
