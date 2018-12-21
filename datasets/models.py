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
    when corresponding `DataFile` object is deleted.
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


class Update(models.Model):
    file = models.ForeignKey(DataFile, on_delete=models.SET_NULL, null=True)
    dataset = models.ForeignKey(Dataset, on_delete=models.SET_NULL, null=True)
    model_name = models.CharField(max_length=255, blank=False, null=False)
    update_date = models.DateTimeField(default=timezone.now)


class HPDViolation(models.Model):
    violation_id = models.IntegerField(blank=False, null=False)
    building_id = models.IntegerField(blank=False, null=False)
    registration_id = models.IntegerField(blank=True, null=True)
    boro_id = models.CharField(blank=False, null=False, max_length=1)
    borough = models.TextField()
    house_number = models.TextField()
    low_house_number = models.TextField()
    high_house_number = models.TextField()
    street_name = models.TextField()
    street_code = models.TextField()
    post_code = models.CharField(max_length=5)
    apartment = models.TextField()
    story = models.TextField()
    block = models.TextField()
    lot = models.TextField()
    class_code = models.CharField(max_length=1)
    inspection_date = models.DateTimeField()
    approved_date = models.DateTimeField()
    original_certify_by_date = models.DateTimeField()
    original_correct_by_date = models.DateTimeField()
    new_certify_by_date = models.DateTimeField()
    new_correct_by_date = models.DateTimeField()
    certified_date = models.DateTimeField()
    order_number = models.TextField()
    nov_id = models.IntegerField()
    nov_description = models.TextField()
    nov_issued_date = models.DateTimeField()
    current_status_id = models.SmallIntegerField()
    current_status = models.TextField()
    current_status_date = models.DateTimeField()
    nov_type = models.TextField()
    violation_status = models.TextField()
    latitude = models.DecimalField(decimal_places=16, max_digits=100)
    longitude = models.DecimalField(decimal_places=16, max_digits=100)
    community_board = models.TextField()
    council_district = models.SmallIntegerField()
    census_tract = models.TextField()
    bin = models.IntegerField()
    bbl = models.CharField(max_length=10, null=False)
    nta = models.TextField()

    @classmethod
    def get_model_fields(self):
        return self._meta.fields

    def __str__(self):
        return self.file.name
