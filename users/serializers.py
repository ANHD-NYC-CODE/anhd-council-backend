from rest_framework import serializers
from django.forms.models import model_to_dict

from users import models as u


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = u.CustomUser
        fields = ('id', 'username', 'email', 'profile', 'groups')

    profile = serializers.SerializerMethodField()
    groups = serializers.StringRelatedField(many=True)

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
        fields = ('email', 'username', 'first_name', 'last_name',
                  'organization', 'description', 'long_description')

    def post(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def validate(self, data):
        """
        Check that the start is before the stop.
        """
        errors = []
        if len(u.CustomUser.objects.filter(email=data['email'])) > 0:
            errors.append(
                "This email is already taken. Please choose another.")

        if len(u.CustomUser.objects.filter(username=data['username'])) > 0 or len(u.UserRequest.objects.filter(username=data['username'])) > 0:
            errors.append(
                "This username is already taken. Please choose another.")

        if len(errors) > 0:
            raise serializers.ValidationError({"errors": errors})
        return data


class AccessRequestSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(many=False, read_only=True)

    class Meta:
        model = u.AccessRequest
        fields = ('user', 'access_type', 'organization_email', 'organization',
                  'position', 'description')

    def validate(self, data):
        """
        Check that the start is before the stop.
        """
        errors = []
        if 'organization_email' in data and len(data['organization_email']) > 0 and (len(u.CustomUser.objects.filter(email=data['organization_email'])) > 0 or len(u.AccessRequest.objects.filter(organization_email=data['organization_email'])) > 0):
            errors.append(
                "This email is already taken. Please choose another.")

        if len(errors) > 0:
            raise serializers.ValidationError({"errors": errors})
        return data


class UserBookmarkedPropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = u.UserBookmarkedProperty
        fields = ('id', 'name', 'bbl')

    def create(self, validated_data):
        return u.UserBookmarkedProperty.objects.create(**validated_data)


# class DistrictDashboardSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = u.DistrictDashboard
#         fields = ['query_string', 'result_hash_digest']

# class UserDistrictDashboardSerializer(serializers.ModelSerializer):
#     district_dashboard_view = DistrictDashboardSerializer()

#     class Meta:
#         model = u.UserDistrictDashboard
#         fields = ('name', 'notification_frequency', 'district_dashboard_view')

#     def create(self, validated_data):
#         return u.UserDistrictDashboard.objects.create(**validated_data)


class UserCustomSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = u.UserCustomSearch
        fields = ('id', 'name', 'notification_frequency', 'custom_search_view', 'created_date')
        extra_kwargs = {'custom_search_view': {'required': False, 'allow_null': True}}

    def to_representation(self, obj):
        rep = super(serializers.ModelSerializer, self).to_representation(obj)
        try:
            rep['custom_search_view'] = obj.custom_search_view.frontend_url
        except:
            rep['custom_search_view'] = ''
        return rep

    def create(self, validated_data):
        try:
            custom_search_view_id = validated_data['custom_search_view']
            validated_data.pop('custom_search_view', None)
            new_user_search = u.UserCustomSearch(**validated_data)
            custom_search = u.CustomSearch.objects.get(id=custom_search_view_id)
            new_user_search.custom_search_view = custom_search
            new_user_search.save()
            return new_user_search
        except Exception as e:
            raise serializers.ValidationError({'detail': e})
