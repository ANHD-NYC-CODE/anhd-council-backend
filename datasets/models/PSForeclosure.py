from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null
from datasets.utils import dates
from django.db.models import Count, OuterRef, Q, Subquery
from django.db.models.functions import Coalesce
from datetime import datetime, timezone
import logging
from datasets import models as ds
from django.db.models import Q

logger = logging.getLogger('app')

# Instructions:
# 1) Login to PropertyShark on 1st of month & download last month's data
# 2) Upload via admin interface


class PSForeclosure(BaseDatasetModel, models.Model):
    QUERY_DATE_KEY = 'dateadded'
    RECENT_DATE_PINNED = True

    class Meta:
        indexes = [
            models.Index(fields=['bbl', '-dateadded']),
            models.Index(fields=['-dateadded']),
        ]

    key = models.TextField(primary_key=True, blank=False, null=False)
    bbl = models.ForeignKey('Property', db_column='bbl', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=False)

    indexno = models.TextField(blank=True, null=True)  # index
    address = models.TextField(blank=True, null=True)  # address
    zipcode = models.TextField(blank=True, null=True)
    neighborhood = models.TextField(blank=True, null=True)
    schooldistrict = models.TextField(blank=True, null=True)
    buildingclass = models.TextField(blank=True, null=True)
    bldgareasqft = models.IntegerField(blank=True, null=True)
    auction = models.DateTimeField(blank=True, null=True)  # auction
    auctiontime = models.TextField(blank=True, null=True)
    auctionlocation = models.TextField(blank=True, null=True)
    dateadded = models.DateTimeField(blank=True, null=True)  # maybe only add if blank?
    plaintiff = models.TextField(blank=True, null=True)
    defendant = models.TextField(blank=True, null=True)
    lien = models.TextField(blank=True, null=True)
    judgment = models.TextField(blank=True, null=True)
    referee = models.TextField(blank=True, null=True)
    plaintiffsattorney = models.TextField(blank=True, null=True)
    foreclosuretype = models.TextField(blank=True, null=True)
    legalprocess = models.TextField(blank=True, null=True)
    hasphoto = models.TextField(blank=True, null=True)
