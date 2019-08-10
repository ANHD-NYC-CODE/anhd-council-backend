from django.db import models
from django.dispatch import receiver
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from datasets.utils import dates
from django.db.models import Count, OuterRef, Q, Subquery
from django.db.models.functions import Coalesce

from datetime import datetime
from core.utils.database import execute
from datasets import models as ds

import logging
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
    lien_type = models.TextField(blank=True, null=True)  # lispendens blank
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
    def annotate_properties(self):
        count = 0
        records = []
        logger.debug('annotating properties for: {}'.format(self.__name__))

        last30 = dates.get_last_month_since_api_update(self.get_dataset(), string=False)
        lastyear = dates.get_last_year(string=False)
        last3years = dates.get_last3years(string=False)

        last30_subquery = Subquery(self.objects.filter(bbl=OuterRef('bbl'), date_added__gte=last30).values(
            'bbl').annotate(count=Count('bbl')).values('count'))

        lastyear_subquery = Subquery(self.objects.filter(bbl=OuterRef(
            'bbl'), date_added__gte=lastyear).values('bbl').annotate(count=Count('bbl')).values('count'))

        last3years_subquery = Subquery(self.objects
                                       .filter(bbl=OuterRef('bbl'), date_added__gte=last3years).values('bbl')
                                       .annotate(count=Count('bbl'))
                                       .values('count')
                                       )

        ds.PropertyAnnotation.objects.update(foreclosures_last30=Coalesce(last30_subquery, 0), foreclosures_lastyear=Coalesce(
            lastyear_subquery, 0), foreclosures_last3years=Coalesce(last3years_subquery, 0), foreclosures_lastupdated=datetime.now())

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
