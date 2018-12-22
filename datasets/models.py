from django.utils import timezone
from django.db import models
from django.dispatch import receiver
from .utils.transform import to_csv
from .utils.utility import dict_to_model


import time
import os
import itertools
BATCH_SIZE = 1000


class Dataset(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    model_name = models.CharField(max_length=255, blank=False, null=False)
    download_endpoint = models.TextField(blank=True, null=True)
    uploaded_date = models.DateTimeField(default=timezone.now)

    def transform_dataset(self, file_path):
        return eval(self.model_name).transform_self(file_path)

    def latest_file(self):
        return self.datafile_set.all()[0]

    def seed_file(self, file_path):
        rows = self.transform_dataset(file_path)

        import pdb
        pdb.set_trace()
        while True:
            batch = list(itertools.islice(rows, 0, BATCH_SIZE))
            if len(batch) == 0:
                break
            else:
                # eval(self.model_name).objects.create_bulk(batch)
                self.db.insert_rows(batch, table_name=eval(self.model_name)._meta.db_table)

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
    violationid = models.IntegerField(blank=False, null=False)
    buildingid = models.IntegerField(blank=False, null=False)
    registrationid = models.IntegerField(blank=True, null=True)
    boroid = models.CharField(blank=False, null=False, max_length=1)
    borough = models.TextField()
    housenumber = models.TextField()
    lowhousenumber = models.TextField()
    highhousenumber = models.TextField()
    streetname = models.TextField()
    streetcode = models.TextField()
    postcode = models.CharField(max_length=5)
    apartment = models.TextField()
    story = models.TextField()
    block = models.TextField()
    lot = models.TextField()
    class_name = models.CharField(db_column='class', max_length=1)
    inspectiondate = models.DateTimeField()
    approveddate = models.DateTimeField()
    originalcertifybydate = models.DateTimeField()
    originalcorrectbydate = models.DateTimeField()
    newcertifybydate = models.DateTimeField()
    newcorrectbydate = models.DateTimeField()
    certifieddate = models.DateTimeField()
    ordernumber = models.TextField()
    novid = models.IntegerField()
    novdescription = models.TextField()
    novissueddate = models.DateTimeField()
    currentstatusid = models.SmallIntegerField()
    currentstatus = models.TextField()
    currentstatusdate = models.DateTimeField()
    novtype = models.TextField()
    violationstatus = models.TextField()
    latitude = models.DecimalField(decimal_places=16, max_digits=100)
    longitude = models.DecimalField(decimal_places=16, max_digits=100)
    communityboard = models.TextField()
    councildistrict = models.SmallIntegerField()
    censustract = models.TextField()
    bin = models.IntegerField()
    bbl = models.CharField(max_length=10, null=False)
    nta = models.TextField()

    @classmethod
    def transform_self(self, file_path):
        return to_csv(file_path)

    @classmethod
    def get_model_fields(self):
        return self._meta.fields

    def __str__(self):
        return self.file.name
