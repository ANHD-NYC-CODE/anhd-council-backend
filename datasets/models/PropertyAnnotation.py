from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel

from datasets import models as ds

import logging
from django.conf import settings
logger = logging.getLogger('app')


class PropertyAnnotation(BaseDatasetModel, models.Model):
    bbl = models.OneToOneField('Property', db_column='bbl', db_constraint=False,
                               on_delete=models.SET_NULL, null=True, blank=True)
    unitsrentstabilized = models.IntegerField(blank=True, null=True)  # from last year of taxbills
    latestsaleprice = models.BigIntegerField(db_index=True, blank=True, null=True)
    # each field is dynamically updated with each dataset update.
    # last year = exactly 12 months from today (or day of last update for corresponding dataset)
    hpdviolations_last30 = models.IntegerField(blank=True, null=True)
    hpdviolations_lastyear = models.IntegerField(blank=True, null=True)
    hpdviolations_last3years = models.IntegerField(blank=True, null=True)
    hpdcomplaints_last30 = models.IntegerField(blank=True, null=True)  # Pinned to 1st of last month of latest data
    hpdcomplaints_lastyear = models.IntegerField(blank=True, null=True)
    hpdcomplaints_last3years = models.IntegerField(blank=True, null=True)
    dobviolations_last30 = models.IntegerField(blank=True, null=True)
    dobviolations_lastyear = models.IntegerField(blank=True, null=True)
    dobviolations_last3years = models.IntegerField(blank=True, null=True)
    dobcomplaints_last30 = models.IntegerField(blank=True, null=True)
    dobcomplaints_lastyear = models.IntegerField(blank=True, null=True)
    dobcomplaints_last3years = models.IntegerField(blank=True, null=True)
    ecbviolations_last30 = models.IntegerField(blank=True, null=True)
    ecbviolations_lastyear = models.IntegerField(blank=True, null=True)
    ecbviolations_last3years = models.IntegerField(blank=True, null=True)
    housinglitigations_last30 = models.IntegerField(blank=True, null=True)
    housinglitigations_lastyear = models.IntegerField(blank=True, null=True)
    housinglitigations_last3years = models.IntegerField(blank=True, null=True)
    dobfiledpermits_last30 = models.IntegerField(blank=True, null=True)
    dobfiledpermits_lastyear = models.IntegerField(blank=True, null=True)
    dobfiledpermits_last3years = models.IntegerField(blank=True, null=True)
    dobissuedpermits_last30 = models.IntegerField(blank=True, null=True)
    dobissuedpermits_lastyear = models.IntegerField(blank=True, null=True)
    dobissuedpermits_last3years = models.IntegerField(blank=True, null=True)
    evictions_last30 = models.IntegerField(blank=True, null=True)
    evictions_lastyear = models.IntegerField(blank=True, null=True)
    evictions_last3years = models.IntegerField(blank=True, null=True)
    acrisrealmasters_last30 = models.IntegerField(blank=True, null=True)
    acrisrealmasters_lastyear = models.IntegerField(blank=True, null=True)
    acrisrealmasters_last3years = models.IntegerField(blank=True, null=True)
    lispendens_last30 = models.IntegerField(blank=True, null=True)
    lispendens_lastyear = models.IntegerField(blank=True, null=True)
    lispendens_last3years = models.IntegerField(blank=True, null=True)
    taxlien = models.BooleanField(blank=True, null=True)
    conhrecord = models.BooleanField(blank=True, null=True)
    nycha = models.BooleanField(blank=True, null=True)
    subsidyj51 = models.BooleanField(blank=True, null=True)
    subsidy421a = models.BooleanField(blank=True, null=True)
    subsidyprograms = models.TextField(blank=True, null=True)
