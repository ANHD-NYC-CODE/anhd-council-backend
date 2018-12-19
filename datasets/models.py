from django.utils import timezone
from django.db import models
import time


class Dataset(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    class_name = models.CharField(max_length=255, blank=False, null=False)
    download_endpoint = models.TextField(blank=True, null=True)
    uploaded_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


def construct_directory_path(instance, filename):
    return '{0}/{1}'.format(instance.dataset.class_name, "{0}-{1}".format(time.time(), filename))


class DataFile(models.Model):
    file = models.FileField(upload_to=construct_directory_path)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    seed_date = models.DateTimeField(blank=True, null=True)
    uploaded_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.file.name
