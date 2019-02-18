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
