from rest_framework import serializers
from django.forms.models import model_to_dict

from core import models as c


class DatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = c.Dataset
        fields = ('name', 'model_name', 'latest_version', 'latest_update')

    latest_update = serializers.SerializerMethodField()
    latest_version = serializers.SerializerMethodField()

    def get_latest_update(self, obj):
        update = obj.latest_update()

        if update:
            return update.completed_date

    def get_latest_version(self, obj):
        return obj.latest_version()
