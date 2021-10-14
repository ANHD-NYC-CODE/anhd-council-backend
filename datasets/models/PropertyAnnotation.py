from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel

from datasets import models as ds

import logging
from django.conf import settings
logger = logging.getLogger('app')


class PropertyAnnotation(BaseDatasetModel, models.Model):

    bbl = models.OneToOneField('Property', db_column='bbl', db_constraint=False,
                               on_delete=models.SET_NULL, null=True, blank=True)
    unitsrentstabilized = models.IntegerField(
        db_index=True, default=0, blank=True, null=True)  # from last year of taxbills
    latestsaleprice = models.BigIntegerField(
        db_index=True, default=0, blank=True, null=True)
    latestsaledate = models.DateTimeField(blank=True, null=True)
    # each field is dynamically updated with each dataset update.
    # last year = exactly 12 months from today (or day of last update for corresponding dataset)
    hpdviolations_last30 = models.IntegerField(
        db_index=True, default=0, blank=True, null=True)
    hpdviolations_lastyear = models.IntegerField(
        db_index=True, default=0, blank=True, null=True)
    hpdviolations_last3years = models.IntegerField(
        db_index=True, default=0, blank=True, null=True)
    hpdviolations_lastupdated = models.DateTimeField(blank=True, null=True)
    # Pinned to 1st of last month of latest data
    hpdcomplaints_last30 = models.IntegerField(
        db_index=True, default=0, blank=True, null=True)
    hpdcomplaints_lastyear = models.IntegerField(
        db_index=True, default=0, blank=True, null=True)
    hpdcomplaints_last3years = models.IntegerField(
        db_index=True, default=0, blank=True, null=True)
    hpdcomplaints_lastupdated = models.DateTimeField(blank=True, null=True)
    dobviolations_last30 = models.IntegerField(
        db_index=True, default=0, blank=True, null=True)
    dobviolations_lastyear = models.IntegerField(
        db_index=True, default=0, blank=True, null=True)
    dobviolations_last3years = models.IntegerField(
        db_index=True, default=0, blank=True, null=True)
    dobviolations_lastupdated = models.DateTimeField(blank=True, null=True)

    dobcomplaints_last30 = models.IntegerField(
        db_index=True, default=0, blank=True, null=True)
    dobcomplaints_lastyear = models.IntegerField(
        db_index=True, default=0, blank=True, null=True)
    dobcomplaints_last3years = models.IntegerField(
        db_index=True, default=0, blank=True, null=True)
    dobcomplaints_lastupdated = models.DateTimeField(blank=True, null=True)

    ecbviolations_last30 = models.IntegerField(
        db_index=True, default=0, blank=True, null=True)
    ecbviolations_lastyear = models.IntegerField(
        db_index=True, default=0, blank=True, null=True)
    ecbviolations_last3years = models.IntegerField(
        db_index=True, default=0, blank=True, null=True)
    ecbviolations_lastupdated = models.DateTimeField(blank=True, null=True)

    housinglitigations_last30 = models.IntegerField(
        db_index=True, default=0, blank=True, null=True)  # pinned to 1st of last month
    housinglitigations_lastyear = models.IntegerField(
        db_index=True, default=0, blank=True, null=True)
    housinglitigations_last3years = models.IntegerField(
        db_index=True, default=0, blank=True, null=True)
    housinglitigations_lastupdated = models.DateTimeField(
        blank=True, null=True)

    dobfiledpermits_last30 = models.IntegerField(
        db_index=True, default=0, blank=True, null=True)
    dobfiledpermits_lastyear = models.IntegerField(
        db_index=True, default=0, blank=True, null=True)
    dobfiledpermits_last3years = models.IntegerField(
        db_index=True, default=0, blank=True, null=True)
    dobfiledpermits_lastupdated = models.DateTimeField(blank=True, null=True)

    dobissuedpermits_last30 = models.IntegerField(
        db_index=True, default=0, blank=True, null=True)
    dobissuedpermits_lastyear = models.IntegerField(
        db_index=True, default=0, blank=True, null=True)
    dobissuedpermits_last3years = models.IntegerField(
        db_index=True, default=0, blank=True, null=True)
    dobissuedpermits_lastupdated = models.DateTimeField(blank=True, null=True)

    evictions_last30 = models.IntegerField(
        db_index=True, default=0, blank=True, null=True)
    evictions_lastyear = models.IntegerField(
        db_index=True, default=0, blank=True, null=True)
    evictions_last3years = models.IntegerField(
        db_index=True, default=0, blank=True, null=True)
    evictions_lastupdated = models.DateTimeField(blank=True, null=True)

    acrisrealmasters_last30 = models.IntegerField(
        db_index=True, default=0, blank=True, null=True)  # pinned to 1st of last month
    acrisrealmasters_lastyear = models.IntegerField(
        db_index=True, default=0, blank=True, null=True)
    acrisrealmasters_last3years = models.IntegerField(
        db_index=True, default=0, blank=True, null=True)
    acrisrealmasters_lastupdated = models.DateTimeField(blank=True, null=True)

    foreclosures_last30 = models.IntegerField(
        db_index=True, default=0, blank=True, null=True)
    foreclosures_lastyear = models.IntegerField(
        db_index=True, default=0, blank=True, null=True)
    foreclosures_last3years = models.IntegerField(
        db_index=True, default=0, blank=True, null=True)
    foreclosures_lastupdated = models.DateTimeField(blank=True, null=True)

    taxlien = models.BooleanField(
        db_index=True, default=False, blank=True, null=True)
    conhrecord = models.BooleanField(
        db_index=True, default=False, blank=True, null=True)
    nycha = models.BooleanField(
        db_index=True, default=False, blank=True, null=True)
    subsidyj51 = models.BooleanField(
        db_index=True, default=False, blank=True, null=True)
    subsidy421a = models.BooleanField(
        db_index=True, default=False, blank=True, null=True)
    subsidyprograms = models.TextField(blank=True, null=True)

    legalclassa = models.IntegerField(db_index=True, blank=True, null=True)
    legalclassb = models.IntegerField(db_index=True, blank=True, null=True)
    managementprogram = models.TextField(
        db_index=True, default='', blank=True, null=True)
    aepstatus = models.TextField(
        db_index=True, default=False, blank=True, null=True)
    aepstartdate = models.DateField(blank=True, null=True)
    aepdischargedate = models.DateField(blank=True, null=True)

    ocahousingcourts_last30 = models.IntegerField(
        db_index=True, default=0, blank=True, null=True)
    ocahousingcourts_lastyear = models.IntegerField(
        db_index=True, default=0, blank=True, null=True)
    ocahousingcourts_last3years = models.IntegerField(
        db_index=True, default=0, blank=True, null=True)
    ocahousingcourts_lastupdated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return str(self.bbl)
