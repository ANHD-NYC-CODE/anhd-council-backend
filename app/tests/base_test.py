from core.models import DataFile
from datasets import models as d_models
from core import models as c_models
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files import File
from django.conf import settings
import os
import zipfile


class BaseTest():
    def clean_tests(self):
        DataFile.objects.all().delete()
        d_models.Property.objects.all().delete()
        d_models.HPDViolation.objects.all().delete()

    def get_file_path(self, name):
        return os.path.join(settings.BASE_DIR, "app/tests/mocks/" + name)

    def update_factory(self, dataset=None, model_name=None, file_name=None, previous_file_name=None):
        if not dataset:
            dataset = c_models.Dataset.objects.create(name=model_name, model_name=model_name)
        file = c_models.DataFile.objects.create(file=self.get_file(file_name), dataset=dataset)

        previous_file = c_models.DataFile.objects.create(file=self.get_file(
            previous_file_name), dataset=dataset) if previous_file_name else None
        update = c_models.Update.objects.create(dataset=dataset, file=file, previous_file=previous_file)
        return update

    def get_file(self, name):
        file_path = os.path.join(settings.BASE_DIR, "app/tests/mocks/" + name)
        file = File(open(file_path, 'rb'))
        file.name = name
        return file
