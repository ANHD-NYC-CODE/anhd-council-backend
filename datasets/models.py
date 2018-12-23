from django.utils import timezone
from django.db import models
from django.dispatch import receiver
from django.apps import apps

from .utils.transform import to_csv
from .utils.utility import dict_to_model
from .utils.database import insert_rows

import time
import os
import itertools

BATCH_SIZE = 1000
ACTIVE_MODELS = ['HPDViolation']
ACTIVE_MODELS_CHOICES = list(map(lambda model: (model, model), ACTIVE_MODELS))


class Dataset(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    model_name = models.CharField(max_length=255, blank=False, null=False, choices=ACTIVE_MODELS_CHOICES)
    download_endpoint = models.TextField(blank=True, null=True)
    uploaded_date = models.DateTimeField(default=timezone.now)

    def transform_dataset(self, file_path):
        return eval(self.model_name).transform_self(file_path)

    def latest_file(self):
        return self.datafile_set.all()[0]

    # from datasets import models; ds = models.Dataset.objects.first(); ds.seed_file(ds.latest_file().file.path);

    def seed_file(self, file_path):
        rows = self.transform_dataset(file_path)
        while True:
            batch = list(itertools.islice(rows, 0, BATCH_SIZE))
            if len(batch) == 0:
                break
            else:
                insert_rows(batch, table_name=eval(self.model_name)._meta.db_table)

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
    model_name = models.CharField(max_length=255, blank=False, null=False,
                                  choices=ACTIVE_MODELS_CHOICES)
    update_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.dataset.name


class HPDViolation(models.Model):
    violationid = models.IntegerField(unique=True, blank=False, null=False)
    buildingid = models.IntegerField(blank=False, null=False)
    registrationid = models.IntegerField(blank=True, null=True)
    boroid = models.CharField(blank=False, null=False, max_length=1)
    borough = models.TextField(db_index=True)
    housenumber = models.TextField()
    lowhousenumber = models.TextField(blank=True, null=True)
    highhousenumber = models.TextField(blank=True, null=True)
    streetname = models.TextField()
    streetcode = models.TextField(blank=True, null=True)
    postcode = models.CharField(max_length=5, blank=True, null=True)
    apartment = models.TextField(blank=True, null=True)
    story = models.TextField(blank=True, null=True)
    block = models.TextField(blank=True, null=True)
    lot = models.TextField(blank=True, null=True)
    class_name = models.CharField(max_length=1)
    inspectiondate = models.DateTimeField(db_index=True, blank=True, null=True)
    approveddate = models.DateTimeField(blank=True, null=True)
    originalcertifybydate = models.DateTimeField(blank=True, null=True)
    originalcorrectbydate = models.DateTimeField(blank=True, null=True)
    newcertifybydate = models.DateTimeField(blank=True, null=True)
    newcorrectbydate = models.DateTimeField(blank=True, null=True)
    certifieddate = models.DateTimeField(blank=True, null=True)
    ordernumber = models.TextField(blank=True, null=True)
    novid = models.IntegerField(blank=True, null=True)
    novdescription = models.TextField(blank=True, null=True)
    novissueddate = models.DateTimeField(blank=True, null=True)
    currentstatusid = models.SmallIntegerField(db_index=True)
    currentstatus = models.TextField(db_index=True)
    currentstatusdate = models.DateTimeField(db_index=True, blank=True, null=True)
    novtype = models.TextField(blank=True, null=True)
    violationstatus = models.TextField(db_index=True)
    latitude = models.DecimalField(decimal_places=8, max_digits=32, blank=True, null=True)
    longitude = models.DecimalField(decimal_places=8, max_digits=32, blank=True, null=True)
    communityboard = models.TextField(blank=True, null=True)
    councildistrict = models.SmallIntegerField(blank=True, null=True)
    censustract = models.TextField(blank=True, null=True)
    bin = models.IntegerField(db_index=True, blank=True, null=True)
    bbl = models.CharField(db_index=True, max_length=10, null=False)
    nta = models.TextField(blank=True, null=True)

    @classmethod
    def transform_self(self, file_path):
        return to_csv(file_path)

    @classmethod
    def get_model_fields(self):
        return self._meta.fields

    def __str__(self):
        return self.name
