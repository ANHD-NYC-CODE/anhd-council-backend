from core.models import DataFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files import File

import os
import zipfile


class BaseTest():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

    def clean_tests(self):
        DataFile.objects.all().delete()

    def get_file_path(self, name):
        return os.path.join(self.BASE_DIR, "app/tests/mocks/" + name)

    def get_file(self, name):

        file_path = os.path.join(self.BASE_DIR, "app/tests/mocks/" + name)

        return File(open(file_path, 'rb'))
