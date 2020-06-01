from django.dispatch import receiver
from datasets import models as ds
from django.db import models
from django.utils import timezone

from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null
import logging
import datetime
logger = logging.getLogger('app')


# Update process: Manual
# Update strategy: Overwrite
#
# Combine all borough files downloaded from DOF into single CSV file
# https://www1.nyc.gov/site/finance/benefits/benefits-421a.page
# upload file through admin, then update

class Subsidy421a(BaseDatasetModel, models.Model):
    bbl = models.ForeignKey('Property', db_column='bbl', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=False)
    borough = models.SmallIntegerField(blank=True, null=True)
    neighborhood = models.TextField(blank=True, null=True)
    buildingclasscategory = models.TextField(blank=True, null=True)
    taxclassatpresent = models.TextField(blank=True, null=True)
    block = models.IntegerField(blank=True, null=True)
    lot = models.IntegerField(blank=True, null=True)
    buildingclassatpresent = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    zipcode = models.TextField(blank=True, null=True)
    residentialunits = models.SmallIntegerField(blank=True, null=True)
    commercialunits = models.SmallIntegerField(blank=True, null=True)
    totalunits = models.SmallIntegerField(blank=True, null=True)
    landsquarefeet = models.IntegerField(blank=True, null=True)
    grosssquarefeet = models.IntegerField(blank=True, null=True)
    yearbuilt = models.SmallIntegerField(db_index=True, blank=True, null=True)

    @classmethod
    def pre_validation_filters(self, gen_rows):
        return gen_rows

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(with_bbl(from_csv_file_to_gen(file_path, update)))

    @classmethod
    def seed_or_update_self(self, **kwargs):
        self.bulk_seed(**kwargs, overwrite=True)

    @classmethod
    def annotate_properties(self):
        for record in self.objects.all():
            try:
                annotation = record.bbl.propertyannotation
                current_programs = annotation.subsidyprograms or ''
                annotation.subsidy421a = True
                annotation.subsidyprograms = ', '.join(
                    filter(None, set([*current_programs.split(', '), '421-a Tax Incentive Program'])))
                annotation.save()
            except Exception as e:
                print(e)

    def __str__(self):
        return str(self.id)


@receiver(models.signals.post_save, sender=Subsidy421a)
def annotate_property_on_save(sender, instance, created, **kwargs):
    if created == True:
        try:
            annotation = instance.bbl.propertyannotation
            annotation.subsidy421a = True
            current_programs = annotation.subsidyprograms or ''
            annotation.subsidyprograms = ', '.join(
                filter(None, set([*current_programs.split(', '), '421a Tax Incentive Program'])))
            annotation.save()
        except Exception as e:
            print(e)
