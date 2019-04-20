from rest_framework import serializers
from django.forms.models import model_to_dict

from users import models as u


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = u.CustomUser
        fields = ('username', 'email', 'profile')

    profile = serializers.SerializerMethodField()

    def get_profile(self, obj):
        profile = obj.userprofile
        return UserProfileSerializer(profile).data


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = u.UserProfile
        fields = ('council',)


class UserRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = u.UserRequest
        fields = ('email', 'username', 'first_name', 'last_name', 'organization', 'description')

    def post(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def validate(self, data):
        """
        Check that the start is before the stop.
        """
        errors = []
        if len(u.CustomUser.objects.filter(email=data['email'])) > 0:
            errors.append("This email is already taken. Please choose another.")

        if len(u.CustomUser.objects.filter(username=data['username'])) > 0 or len(u.UserRequest.objects.filter(username=data['username'])) > 0:
            errors.append("This username is already taken. Please choose another.")

        if len(errors) > 0:
            raise serializers.ValidationError({"errors": errors})
        return data
