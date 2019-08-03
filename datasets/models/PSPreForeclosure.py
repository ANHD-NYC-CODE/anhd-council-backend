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


class PSPreForeclosure(BaseDatasetModel, models.Model):
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

    address = models.TextField(blank=True, null=True)  # address
    indexno = models.TextField(blank=True, null=True)  # index
    zipcode = models.TextField(blank=True, null=True)
    creditor = models.TextField(blank=True, null=True)  # creditor
    neighborhood = models.TextField(blank=True, null=True)
    documenttype = models.TextField(blank=True, null=True)
    schooldistrict = models.TextField(blank=True, null=True)
    lientype = models.TextField(blank=True, null=True)
    buildingclass = models.TextField(blank=True, null=True)
    taxvalue = models.TextField(blank=True, null=True)
    dateadded = models.DateTimeField(blank=True, null=True)  # date_added
    bldgareasqft = models.IntegerField(blank=True, null=True)
    debtor = models.TextField(blank=True, null=True)  # debtor
    debtoraddress = models.TextField(blank=True, null=True)
    mortgagedate = models.DateTimeField(blank=True, null=True)  # mortgage_date
    mortgageamount = models.IntegerField(blank=True, null=True)  # mortgage_amount
    hasphoto = models.TextField(blank=True, null=True)
