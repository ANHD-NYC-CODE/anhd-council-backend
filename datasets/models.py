from django.utils import timezone
from django.db import models
from django.dispatch import receiver
from django.apps import apps

from .utils.transform import to_csv, extract_csvs_from_zip, with_geo, remove_non_residential
from .utils.utility import dict_to_model
from .utils.database import insert_rows

import time
import os
import itertools

BATCH_SIZE = 1000
ACTIVE_MODELS = ['HPDViolation', 'Pluto18v1']
ACTIVE_MODELS_CHOICES = list(map(lambda model: (model, model), ACTIVE_MODELS))


class Dataset(models.Model):
    name = models.CharField(unique=True, max_length=255, blank=False, null=False)
    model_name = models.CharField(unique=True, max_length=255, blank=False, null=False, choices=ACTIVE_MODELS_CHOICES)
    download_endpoint = models.TextField(blank=True, null=True)
    uploaded_date = models.DateTimeField(default=timezone.now)

    def transform_dataset(self, file_path):
        return eval(self.model_name).transform_self(file_path)

    def latest_file(self):
        return self.datafile_set.latest('uploaded_date')

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


class Pluto18v1(models.Model):
    # from datasets import models; ds = models.Dataset.objects.filter(model_name='Plutov18v1'); ds.seed_file(ds.latest_file().file.path);

    borough = models.TextField(blank=False, null=False)
    block = models.TextField(blank=False, null=False)
    lot = models.TextField(blank=False, null=False)
    cd = models.SmallIntegerField(blank=False, null=False)
    ct2010 = models.TextField(blank=True, null=True)
    cb2010 = models.TextField(blank=True, null=True)
    schooldist = models.SmallIntegerField(blank=True, null=True)
    council = models.SmallIntegerField(db_index=True, blank=False, null=False)
    zipcode = models.CharField(max_length=5, blank=False, null=False)
    firecomp = models.TextField(blank=True, null=True)
    policeprct = models.TextField(blank=True, null=True)
    healthcenterdistrict = models.SmallIntegerField(blank=True, null=True)
    healtharea = models.TextField(blank=True, null=True)
    sanitboro = models.CharField(max_length=1, blank=True, null=True)
    sanitdistrict = models.SmallIntegerField(blank=True, null=True)
    sanitsub = models.CharField(max_length=2, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    original_address = models.TextField(blank=True, null=True)
    zonedist1 = models.TextField(blank=True, null=True)
    zonedist2 = models.TextField(blank=True, null=True)
    zonedist3 = models.TextField(blank=True, null=True)
    zonedist4 = models.TextField(blank=True, null=True)
    overlay1 = models.TextField(blank=True, null=True)
    overlay2 = models.TextField(blank=True, null=True)
    spdist1 = models.TextField(blank=True, null=True)
    spdist2 = models.TextField(blank=True, null=True)
    spdist3 = models.TextField(blank=True, null=True)
    ltdheight = models.TextField(blank=True, null=True)
    splitzone = models.BooleanField(blank=True, null=True)
    bldgclass = models.CharField(db_index=True, max_length=2, blank=False, null=False)
    landuse = models.SmallIntegerField(blank=True, null=True)
    easements = models.TextField(blank=True, null=True)
    ownertype = models.CharField(max_length=1, blank=True, null=True)
    ownername = models.TextField(blank=True, null=True)
    lotarea = models.BigIntegerField(blank=True, null=True)
    bldgarea = models.BigIntegerField(blank=True, null=True)
    comarea = models.BigIntegerField(blank=True, null=True)
    resarea = models.BigIntegerField(blank=True, null=True)
    officearea = models.BigIntegerField(blank=True, null=True)
    retailarea = models.BigIntegerField(blank=True, null=True)
    garagearea = models.BigIntegerField(blank=True, null=True)
    strgearea = models.BigIntegerField(blank=True, null=True)
    factryarea = models.BigIntegerField(blank=True, null=True)
    otherarea = models.BigIntegerField(blank=True, null=True)
    areasource = models.TextField(blank=True, null=True)
    numbldgs = models.IntegerField(db_index=True, blank=True, null=True)
    numfloors = models.DecimalField(db_index=True, decimal_places=2, max_digits=8, blank=True, null=True)
    unitsres = models.IntegerField(db_index=True, blank=False, null=False)
    unitstotal = models.IntegerField(db_index=True, blank=False, null=False)
    lotfront = models.DecimalField(decimal_places=3, max_digits=32, blank=True, null=True)
    lotdepth = models.DecimalField(decimal_places=3, max_digits=32, blank=True, null=True)
    bldgfront = models.DecimalField(decimal_places=3, max_digits=32, blank=True, null=True)
    bldgdepth = models.DecimalField(decimal_places=3, max_digits=32, blank=True, null=True)
    ext = models.TextField(blank=True, null=True)
    proxcode = models.CharField(max_length=1, blank=True, null=True)
    irrlotcode = models.BooleanField(blank=True, null=True)
    lottype = models.CharField(max_length=1, blank=True, null=True)
    bsmtcode = models.CharField(max_length=1, blank=True, null=True)
    assessland = models.BigIntegerField(blank=True, null=True)
    assesstot = models.BigIntegerField(blank=True, null=True)
    exemptland = models.BigIntegerField(blank=True, null=True)
    exempttot = models.BigIntegerField(blank=True, null=True)
    yearbuilt = models.SmallIntegerField(db_index=True, blank=False, null=False)
    yearalter1 = models.SmallIntegerField(blank=True, null=True)
    yearalter2 = models.SmallIntegerField(blank=True, null=True)
    histdist = models.TextField(blank=True, null=True)
    landmark = models.TextField(blank=True, null=True)
    builtfar = models.DecimalField(db_index=True, decimal_places=2, max_digits=8, blank=True, null=True)
    residfar = models.DecimalField(db_index=True, decimal_places=2, max_digits=8, blank=True, null=True)
    commfar = models.DecimalField(db_index=True, decimal_places=2, max_digits=8, blank=True, null=True)
    facilfar = models.DecimalField(db_index=True, decimal_places=2, max_digits=8, blank=True, null=True)
    borocode = models.CharField(db_index=True, max_length=1, blank=False, null=False)
    bbl = models.CharField(db_index=True, unique=True, max_length=10, blank=False, null=False)
    condono = models.TextField(blank=True, null=True)
    tract2010 = models.TextField(blank=True, null=True)
    xcoord = models.IntegerField(blank=True, null=True)
    ycoord = models.IntegerField(blank=True, null=True)
    zonemap = models.TextField(blank=True, null=True)
    zmcode = models.CharField(max_length=1, blank=True, null=True)
    sanborn = models.TextField(blank=True, null=True)
    taxmap = models.TextField(blank=True, null=True)
    edesignum = models.TextField(blank=True, null=True)
    appbbl = models.CharField(db_index=True, max_length=10, blank=True, null=True)
    appdate = models.DateTimeField(blank=True, null=True)
    plutomapid = models.CharField(max_length=1, blank=True, null=True)
    firm07flag = models.CharField(max_length=1, blank=True, null=True)
    pfirm15flag = models.CharField(max_length=1, blank=True, null=True)
    version = models.TextField(blank=True, null=True)
    lng = models.DecimalField(decimal_places=16, max_digits=32, blank=True, null=True)
    lat = models.DecimalField(decimal_places=16, max_digits=32, blank=True, null=True)

    @classmethod
    def transform_self(self, file_path):
        return with_geo(remove_non_residential(to_csv(extract_csvs_from_zip(file_path))))

    def __str__(self):
        return self.bbl


class Building:
    x = eval(Dataset.objects.get(name="Buildings").model_name)


# class HPDViolation(models.Model):
#     # from datasets import models; ds = models.Dataset.objects.first(); ds.seed_file(ds.latest_file().file.path);
#     violationid = models.IntegerField(unique=True, blank=False, null=False)
#     buildingid = models.IntegerField(blank=False, null=False)
#     registrationid = models.IntegerField(blank=True, null=True)
#     boroid = models.CharField(blank=False, null=False, max_length=1)
#     borough = models.TextField(db_index=True)
#     housenumber = models.TextField()
#     lowhousenumber = models.TextField(blank=True, null=True)
#     highhousenumber = models.TextField(blank=True, null=True)
#     streetname = models.TextField()
#     streetcode = models.TextField(blank=True, null=True)
#     postcode = models.CharField(max_length=5, blank=True, null=True)
#     apartment = models.TextField(blank=True, null=True)
#     story = models.TextField(blank=True, null=True)
#     block = models.TextField(blank=True, null=True)
#     lot = models.TextField(blank=True, null=True)
#     class_name = models.CharField(max_length=1)
#     inspectiondate = models.DateTimeField(db_index=True, blank=True, null=True)
#     approveddate = models.DateTimeField(blank=True, null=True)
#     originalcertifybydate = models.DateTimeField(blank=True, null=True)
#     originalcorrectbydate = models.DateTimeField(blank=True, null=True)
#     newcertifybydate = models.DateTimeField(blank=True, null=True)
#     newcorrectbydate = models.DateTimeField(blank=True, null=True)
#     certifieddate = models.DateTimeField(blank=True, null=True)
#     ordernumber = models.TextField(blank=True, null=True)
#     novid = models.IntegerField(blank=True, null=True)
#     novdescription = models.TextField(blank=True, null=True)
#     novissueddate = models.DateTimeField(blank=True, null=True)
#     currentstatusid = models.SmallIntegerField(db_index=True)
#     currentstatus = models.TextField(db_index=True)
#     currentstatusdate = models.DateTimeField(db_index=True, blank=True, null=True)
#     novtype = models.TextField(blank=True, null=True)
#     violationstatus = models.TextField(db_index=True)
#     latitude = models.DecimalField(decimal_places=8, max_digits=32, blank=True, null=True)
#     longitude = models.DecimalField(decimal_places=8, max_digits=32, blank=True, null=True)
#     communityboard = models.TextField(blank=True, null=True)
#     councildistrict = models.SmallIntegerField(blank=True, null=True)
#     censustract = models.TextField(blank=True, null=True)
#     bin = models.IntegerField(db_index=True, blank=True, null=True)
#     bbl = models.CharField(db_index=True, max_length=10, null=False)
#     nta = models.TextField(blank=True, null=True)
#
#     @classmethod
#     def transform_self(self, file_path):
#         return to_csv(file_path)
#
#     def __str__(self):
#         return self.name
