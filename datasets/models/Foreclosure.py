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

# Update Instructions:
# 1. Login to Property Shark on 1st of the month
# 2. Download Foreclosures AND Preforeclosures from last month
# 3. upload PSPreforeclosures first, PSForeclosures second
# 4. create an update for Foreclosure


class Foreclosure(BaseDatasetModel, models.Model):
    QUERY_DATE_KEY = 'date_added'
    RECENT_DATE_PINNED = True

    class Meta:
        indexes = [
            models.Index(fields=['bbl', '-date_added']),
            models.Index(fields=['-date_added']),
        ]

    key = models.TextField(primary_key=True, blank=False, null=False)
    bbl = models.ForeignKey('Property', db_column='bbl', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=False)
    index = models.TextField(unique=True, blank=False, null=False)
    address = models.TextField(blank=True, null=True)
    document_type = models.TextField(blank=True, null=True)
    lien_type = models.TextField(blank=True, null=True)  # legacy blank
    # entereddate in LisPenden and date_added for PropertyShark
    date_added = models.DateTimeField(blank=True, null=True)
    creditor = models.TextField(blank=True, null=True)
    debtor = models.TextField(blank=True, null=True)
    mortgage_date = models.TextField(blank=True, null=True)
    mortgage_amount = models.TextField(blank=True, null=True)
    auction = models.DateTimeField(blank=True, null=True)  # only from PropertySharkForeclosure
    foreign_key = models.TextField(blank=True, null=True)
    source = models.TextField(blank=True, null=True)  # PDC or PropertyShark

    @classmethod
    def seed_or_update_self(self, **kwargs):
        logger.debug("Seeding/Updating {}", self.__name__)
        # Add records PSForeclosure and PSPreForeclosure

    @classmethod
    def annotate_properties(self):
        self.annotate_all_properties_month_offset()

    def __str__(self):
        return str(self.key)


@receiver(models.signals.post_save, sender=Foreclosure)
def annotate_property_on_save(sender, instance, created, **kwargs):
    if created == True:
        try:
            annotation = sender.annotate_property_standard(ds.PropertyAnnotation.objects.get(bbl=instance.bbl))
            annotation.save()
        except Exception as e:
            print(e)
