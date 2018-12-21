from django.utils import timezone
from django.db import models
from django.dispatch import receiver

import time
import os


class Dataset(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    model_name = models.CharField(max_length=255, blank=False, null=False)
    download_endpoint = models.TextField(blank=True, null=True)
    uploaded_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


def construct_directory_path(instance, filename):
    return '{0}/{1}'.format('./', "{0}-{1}".format(time.time(), filename))


class DataFile(models.Model):
    file = models.FileField(upload_to=construct_directory_path)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    seed_date = models.DateTimeField(blank=True, null=True)
    uploaded_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.file.name


@receiver(models.signals.post_delete, sender=DataFile)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


class Update(models.Model):
    file = models.ForeignKey(DataFile, on_delete=models.SET_NULL, null=True)
    dataset = models.ForeignKey(Dataset, on_delete=models.SET_NULL, null=True)
    model_name = models.CharField(max_length=255, blank=False, null=False)
    update_date = models.DateTimeField(default=timezone.now)

#
# class HPDViolation(models.Model):
#
#     def __str__(self):
#         return self.file.name
