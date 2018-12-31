from core.models import DataFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files import File
from django.conf import settings
import os
import zipfile


class BaseTest():
    def clean_tests(self):
        return
        DataFile.objects.all().delete()

    def get_file_path(self, name):
        return os.path.join(settings.BASE_DIR, "app/tests/mocks/" + name)

    def get_file(self, name):
        file_path = os.path.join(settings.BASE_DIR, "app/tests/mocks/" + name)
        file = File(open(file_path, 'rb'))
        file.name = name
        return file
