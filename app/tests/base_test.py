from core.models import DataFile
from django.core.files.uploadedfile import SimpleUploadedFile

import os


class BaseTest():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

    def clean_tests(self):
        DataFile.objects.all().delete()

    def get_file_path(self, name):
        return os.path.join(self.BASE_DIR, "app/tests/mocks/" + name)

    def get_file(self, name):
        test_file = os.path.join(self.BASE_DIR, "app/tests/mocks/" + name)
        return SimpleUploadedFile(name, open(test_file, 'r').read().encode('utf-8'))
