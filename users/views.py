from django.shortcuts import render
from django.http import QueryDict
from django.shortcuts import get_object_or_404, redirect
from django.conf import settings
from rest_framework import viewsets
from datasets.helpers.api_helpers import ApplicationViewSet
from datasets.utils.advanced_filter import fe_to_be_url
from rest_framework.permissions import IsAuthenticated
from app.tasks import get_query_result_hash_and_length
from users import models as u
from users import serializers as serial
from rest_framework.response import Response
from rest_framework import generics, mixins, status
from users.tokens import password_reset_token

import hashlib


class UserVerifyView(generics.GenericAPIView):
    serializer_class = serial.UserSerializer

    def get(self, request, username, verification_token):
        user = get_object_or_404(u.CustomUser, username=username)
        if password_reset_token.check_token(user, verification_token):
            access_request = u.AccessRequest.objects.filter(user_id=user.id)[0]
            access_request.add_user_to_trusted()
            user.email = access_request.organization_email
            user.save()

            root_url = 'http://localhost:8000/' if settings.DEBUG else 'https://portal.displacementalert.org/'
            return redirect(root_url)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class UserRegisterView(mixins.CreateModelMixin,
                       generics.GenericAPIView):

    serializer_class = serial.UserSerializer

    def post(self, request, *args, **kwargs):
        data_dict = request.data

        if not ('username' in data_dict and 'email' in data_dict and 'first_name' in data_dict and 'last_name' in data_dict):
            return Response('Your request must include username, email, first_name, last_name.', status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        if u.CustomUser.objects.filter(username=request.data):
            return Response('This username is already taken', status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        new_user = u.CustomUser(
            username=data_dict['username'],
            email=data_dict['email'],
            first_name=data_dict['first_name'],
            last_name=data_dict['last_name'],
            is_staff=False
        )
        new_user.save()
        from app.tasks import async_send_new_user_email
        async_send_new_user_email.delay(new_user.id)
        return Response('User created successfully. Check your email for verification.', status=status.HTTP_201_CREATED)


class UserViewSet(ApplicationViewSet, viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = u.CustomUser.objects.all()
    pagination_class = None

    def get_current_user(self, request, *args, **kwargs):
        serializer = serial.UserSerializer(request.user)
        response_data = serializer.data

        # Add access request status
        if u.AccessRequest.objects.filter(user_id=request.user.id):
            access_request = u.AccessRequest.objects.filter(user_id=request.user.id)[0]
            if access_request.approved:
                response_data['accessRequestStatus'] = 'approved'
            else:
                response_data['accessRequestStatus'] = 'pending'
        else:
            response_data['accessRequestStatus'] = None

        return Response(response_data)


class UserRequestViewSet(ApplicationViewSet,
                         mixins.CreateModelMixin,
                         viewsets.GenericViewSet):
    queryset = u.UserRequest.objects.all()
    serializer_class = serial.UserRequestSerializer


class AccessRequestCollection(mixins.CreateModelMixin,
                              generics.GenericAPIView):

    queryset = u.AccessRequest.objects.all()
    serializer_class = serial.AccessRequestSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        data_dict = request.data
        mutable_query_dict = QueryDict(mutable=True)
        mutable_query_dict.update(data_dict)
        mutable_query_dict.__setitem__('user_id', request.user.id)

        if u.AccessRequest.objects.filter(user_id=request.user.id):
            return Response('A user can only make one access request', status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        serializer = self.get_serializer(data=mutable_query_dict)
        serializer.is_valid(raise_exception=True)
        serializer.create(validated_data=mutable_query_dict.dict())
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def delete(self, request, *args, **kwargs):
        user_id = request.user.id

        if u.AccessRequest.objects.filter(user_id=request.user.id):
            access_request = u.AccessRequest.objects.get(user_id=request.user.id)
            access_request.delete()
            return Response('The user access request has been deleted', status=status.HTTP_204_NO_CONTENT)
        else:
            return Response('This user has no pending request', status=status.HTTP_404_NOT_FOUND)


class UserBookmarkedPropertyCollection(mixins.ListModelMixin,
                                       mixins.CreateModelMixin,
                                       generics.GenericAPIView):

    queryset = u.UserBookmarkedProperty.objects.all()
    serializer_class = serial.UserBookmarkedPropertySerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = request.user
        queryset = u.UserBookmarkedProperty.objects.filter(user_id=user)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        data_dict = request.data
        mutable_query_dict = QueryDict(mutable=True)
        mutable_query_dict.update(data_dict)
        mutable_query_dict.__setitem__('user_id', request.user.id)

        if u.UserBookmarkedProperty.objects.filter(user_id=request.user.id, bbl=data_dict['bbl']):
            return Response("User has already bookmarked this property", status=status.HTTP_422_UNPROCESSABLE_ENTITY)

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
        data_dict = request.data
        mutable_query_dict = QueryDict(mutable=True)
        mutable_query_dict.update(data_dict)
        mutable_query_dict.__setitem__('user_id', request.user.id)
        custom_search_query_fe = mutable_query_dict.__getitem__('custom_search_view')
        custom_search_query = fe_to_be_url(custom_search_query_fe)

        # Get custom search or create
        # Search for CustomSearch by hash
        query_hash_digest = hashlib.sha256(custom_search_query.encode('utf-8')).hexdigest()
        try:
            result_hash_length = get_query_result_hash_and_length(custom_search_query)
            result_hash = result_hash_length['hash']
        except Exception as e:
            return Response('The query submitted is not valid', status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        if u.CustomSearch.objects.filter(query_string_hash_digest=query_hash_digest).exists():
            custom_search = u.CustomSearch.objects.get(query_string_hash_digest=query_hash_digest)
        else:
            custom_search = u.CustomSearch(
                frontend_url=custom_search_query_fe,
                query_string=custom_search_query,
                result_hash_digest=result_hash
            )
            custom_search.save()
        mutable_query_dict.__setitem__('last_number_of_results', result_hash_length['length'])
        mutable_query_dict.__setitem__('custom_search_view', custom_search.id)
        mutable_query_dict.__setitem__('last_notified_hash', custom_search.result_hash_digest)

        serializer = self.get_serializer(data=mutable_query_dict)
        serializer.is_valid(raise_exception=True)

        serializer.create(validated_data=mutable_query_dict.dict())

        return Response(status=status.HTTP_201_CREATED)

class UserCustomSearchMember(mixins.DestroyModelMixin,
                             mixins.UpdateModelMixin,
                             generics.GenericAPIView):

    queryset = u.UserCustomSearch.objects.all()
    serializer_class = serial.UserCustomSearchSerializer
    permission_classes = (IsAuthenticated,)

    def patch(self, request, *args, **kwargs):
        data_dict = request.data
        mutable_query_dict = QueryDict(mutable=True)
        mutable_query_dict.update(data_dict)
        mutable_query_dict.__setitem__('user_id', request.user.id)

        instance = self.get_object()

        if 'custom_search_view' in mutable_query_dict.keys():
            custom_search_query_fe = mutable_query_dict.__getitem__('custom_search_view')
            custom_search_query = fe_to_be_url(custom_search_query_fe)

            query_hash_digest = hashlib.sha256(custom_search_query.encode('utf-8')).hexdigest()

            try:
                result_hash_length = get_query_result_hash_and_length(custom_search_query)
                result_hash = result_hash_length['hash']
            except Exception as e:
                Response('The query submitted is not valid', status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            if u.CustomSearch.objects.filter(query_string_hash_digest=query_hash_digest).exists():
                custom_search = u.CustomSearch.objects.get(query_string_hash_digest=query_hash_digest)
            else:
                custom_search = u.CustomSearch(
                    frontend_url=custom_search_query_fe,
                    query_string=custom_search_query,
                    result_hash_digest=result_hash
                )
                custom_search.save()
            mutable_query_dict.__setitem__('custom_search_view', custom_search.id)
            mutable_query_dict.__setitem__('last_notified_hash', custom_search.result_hash_digest)
            mutable_query_dict.__setitem__('last_number_of_results', result_hash_length['length'])

        serializer = self.get_serializer(instance, data=mutable_query_dict)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

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
