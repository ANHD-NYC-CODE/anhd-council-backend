from django.dispatch import receiver
from datasets import models as ds
from django.db import models
from django.utils import timezone

from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_xlsx_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null
import logging
import datetime
import re
logger = logging.getLogger('app')


# Update process: Manual
# Update strategy: Overwrite
#
# Download Core Data "Full Property and Subsidy Dataset"
# https://nyu.box.com/shared/static/a3zb4u588l06jmz1jwuep400womyc85q.zip
# Extract ZIP and upload xlsx file through admin, then update
# Please make sure to add new fields to this model and migrate to live site when needed, ie "serviolation2021" and "taxdelinquency2021" as it changes yearly

class CoreSubsidyRecord(BaseDatasetModel, models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['bbl', 'programname']),
            models.Index(fields=['bbl', 'enddate']),
        ]

    bbl = models.ForeignKey('Property', db_column='bbl', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=False)
    fcsubsidyid = models.BigIntegerField(blank=True, null=True)
    agencysuppliedid1 = models.TextField(blank=True, null=True)
    agencysuppliedid2 = models.TextField(blank=True, null=True)
    agencyname = models.TextField(blank=True, null=True)
    regulatorytool = models.TextField(blank=True, null=True)
    programname = models.TextField(db_index=True, blank=True, null=True)
    projectname = models.TextField(blank=True, null=True)
    preservation = models.TextField(blank=True, null=True)
    tenure = models.TextField(blank=True, null=True)
    startdate = models.DateField(blank=True, null=True)
    enddate = models.DateField(db_index=True, blank=True, null=True)
    reacscore = models.TextField(blank=True, null=True)
    reacdate = models.DateField(blank=True, null=True)
    cdid = models.SmallIntegerField(blank=True, null=True)
    ccdid = models.SmallIntegerField(blank=True, null=True)
    pumaid = models.SmallIntegerField(blank=True, null=True)
    tract10id = models.BigIntegerField(blank=True, null=True)
    boroname = models.TextField(blank=True, null=True)
    cdname = models.TextField(blank=True, null=True)
    ccdname = models.TextField(blank=True, null=True)
    pumaname = models.TextField(blank=True, null=True)
    assessedvalue = models.BigIntegerField(blank=True, null=True)
    yearbuilt = models.SmallIntegerField(blank=True, null=True)
    ownername = models.TextField(blank=True, null=True)
    resunits = models.SmallIntegerField(blank=True, null=True)
    standardaddress = models.TextField(blank=True, null=True)
    buildings = models.SmallIntegerField(blank=True, null=True)
    serviolation2017 = models.SmallIntegerField(blank=True, null=True)
    taxdelinquency2016 = models.SmallIntegerField(blank=True, null=True)
    serviolation2018 = models.SmallIntegerField(blank=True, null=True)
    taxdelinquency2018 = models.SmallIntegerField(blank=True, null=True)
    serviolation2019 = models.SmallIntegerField(blank=True, null=True)
    taxdelinquency2019 = models.SmallIntegerField(blank=True, null=True)
    serviolation2021 = models.SmallIntegerField(blank=True, null=True)
    taxdelinquency2021 = models.SmallIntegerField(blank=True, null=True)
    dataoutputdate = models.DateField(blank=True, null=True)
    longitude = models.DecimalField(
        decimal_places=8, max_digits=16, blank=True, null=True)
    latitude = models.DecimalField(
        decimal_places=8, max_digits=16, blank=True, null=True)

    slim_query_fields = ["id", "bbl", "programname", "enddate"]

    @classmethod
    def standardize_programnames(self, row):
        # Raw:
        # 420-c Tax Incentive Program
        # 421-a Affordable
        # 421-a Tax Incentive Program
        # 421-g Tax Incentive Program
        # Article 8A/HRP
        # Federal Public Housing
        # Inclusionary Housing
        # J-51 Tax Incentive
        # LAMP - HDC
        # LIHTC 4%
        # LIHTC 9%
        # LIHTC Year 15
        # Loan Management Set-Aside
        # Mitchell-Lama
        # Multi-Family Program
        # Neighborhood Entrepreneur Program
        # Neighborhood Redevelopment Program
        # NYCHA - Mixed Financing
        # Other HPD Programs
        # Other HUD Financing
        # Other HUD Project-Based Rental Assistance
        # Participation Loan Program
        # Project-Based Section 8
        # Project Rental Assistance Contract / 202
        # Section 202/8
        # Section 221d(3) and Section 221d(4) Mortgage Insurance
        # Section 223(f)
        # Section 8 - RAD
        # TPT

        # row['programname'] = re.sub(r"\b421a\b", "421-a", row['programname'])
        return row

    @classmethod
    def pre_validation_filters(self, gen_rows):
        # Clean and standardize the program names
        for row in gen_rows:
            if row['programname'] == 'NYCHA - Mixed Financing' or row['programname'] == 'Federal Public Housing':
                continue

            yield row

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(from_xlsx_file_to_gen(file_path, 'SubsidizedHousingDatabase', update))

    @classmethod
    def seed_or_update_self(self, **kwargs):
        self.bulk_seed(**kwargs, overwrite=True)

    @classmethod
    def annotate_properties(self):
        for record in self.objects.all():
            try:
                annotation = record.bbl.propertyannotation
                current_programs = annotation.subsidyprograms or ''
                annotation.subsidyprograms = ', '.join(
                    filter(None, set([*current_programs.split(', '), record.programname])))

                annotation.save()
            except Exception as e:
                print(e)

    def __str__(self):
        return str(self.id)


@receiver(models.signals.post_save, sender=CoreSubsidyRecord)
def annotate_property_on_save(sender, instance, created, **kwargs):
    if created == True:
        try:
            annotation = instance.bbl.propertyannotation
            current_programs = annotation.subsidyprograms or ''
            annotation.subsidyprograms = ', '.join(
                filter(None, set([*current_programs.split(', '), instance.programname])))

            annotation.save()
        except Exception as e:
            print(e)
