from django.shortcuts import render
from django.http import QueryDict
from rest_framework import viewsets
from datasets.helpers.api_helpers import ApplicationViewSet
from rest_framework.permissions import IsAuthenticated
from core.tasks import get_query_result_hash
from users import models as u
from users import serializers as serial
from rest_framework.response import Response
from rest_framework import generics, mixins, status

import hashlib


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


class UserBookmarkedPropertyCollection(mixins.ListModelMixin,
                                         mixins.CreateModelMixin,
                                         generics.GenericAPIView):

    queryset = u.UserBookmarkedProperty.objects.all()
    serializer_class = serial.UserBookmarkedPropertySerializer
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


class UserBookmarkedPropertyMember(mixins.DestroyModelMixin,
                                     generics.GenericAPIView):

    queryset = u.UserBookmarkedProperty.objects.all()
    serializer_class = serial.UserBookmarkedPropertySerializer
    permission_classes = (IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user == request.user:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


# class UserDistrictDashboardView(mixins.ListModelMixin,
#                                 mixins.CreateModelMixin,
#                                 mixins.DestroyModelMixin,
#                                 generics.GenericAPIView):

#     queryset = u.UserDistrictDashboard.objects.all()
#     serializer_class = serial.UserDistrictDashboardSerializer
#     permission_classes = (IsAuthenticated,)

#     def get(self, request, *args, **kwargs):
#         user = request.user
#         queryset = user.userdistrictdashboard_set.all()

#         page = self.paginate_queryset(queryset)
#         if page is not None:
#             serializer = self.get_serializer(page, many=True)
#             return self.get_paginated_response(serializer.data)

#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)

#     def post(self, request, *args, **kwargs):
#         data_dict = request.data.dict()
#         mutable_query_dict = QueryDict(mutable=True)
#         mutable_query_dict.update(data_dict)
#         mutable_query_dict.__setitem__('user_id', request.user.id)

#         serializer = self.get_serializer(data=mutable_query_dict)
#         serializer.is_valid(raise_exception=True)



#         serializer.create(validated_data=mutable_query_dict.dict())
#         headers = self.get_success_headers(serializer.data)
#         return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

#     def delete(self, request, *args, **kwargs):
#         instance = self.get_object()
#         if instance.user == request.user:
#             self.perform_destroy(instance)
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         else:
#             return Response(status=status.HTTP_404_NOT_FOUND)


class UserCustomSearchCollection(mixins.ListModelMixin,
                                mixins.CreateModelMixin,
                                generics.GenericAPIView):

    queryset = u.UserCustomSearch.objects.all()
    serializer_class = serial.UserCustomSearchSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = request.user
        queryset = user.usercustomsearch_set.all()

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
        custom_search_query = mutable_query_dict.__getitem__('custom_search_view')

        # Get custom search or create
        # Search for CustomSearch by hash
        query_hash_digest = hashlib.sha256(custom_search_query.encode('utf-8')).hexdigest()
        if u.CustomSearch.objects.filter(query_string_hash_digest=query_hash_digest).exists():
            custom_search = u.CustomSearch.objects.get(query_string_hash_digest=query_hash_digest)
        else:
            try:
                result_hash = get_query_result_hash(custom_search_query)
            except Exception as e:
                Response('The query submitted is not valid', status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            custom_search = u.CustomSearch(query_string=custom_search_query, result_hash_digest=result_hash)
            custom_search.save()
        mutable_query_dict.__setitem__('custom_search_view', custom_search.id)
        mutable_query_dict.__setitem__('last_notified_hash', custom_search.result_hash_digest)

        serializer = self.get_serializer(data=mutable_query_dict)
        serializer.is_valid(raise_exception=True)

        serializer.create(validated_data=mutable_query_dict.dict())

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class UserCustomSearchMember(mixins.DestroyModelMixin,
                                generics.GenericAPIView):

    queryset = u.UserCustomSearch.objects.all()
    serializer_class = serial.UserCustomSearchSerializer
    permission_classes = (IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user == request.user:
            custom_search_view = instance.custom_search_view
            users_of_search = u.UserCustomSearch.objects.filter(custom_search_view=custom_search_view.id)

            # If this user is the only one using a search delete it
            if len(users_of_search) == 1:
                custom_search_view.delete()

            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
