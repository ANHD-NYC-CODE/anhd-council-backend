from django.db import models
from django.dispatch import receiver
from datasets.utils.BaseDatasetModel import BaseDatasetModel

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
    def upsert_permit_sql(self, other_table, cols):
        table_name = self._meta.db_table
        primary_key = self._meta.pk.name
        other_table_name = other_table._meta.db_table
        fields = ', '.join([k.name for k in self._meta.get_fields()])
        upsert_fields = ', '.join([k.name + "=EXCLUDED." + k.name for k in self._meta.get_fields()])

        sql = "INSERT INTO {table_name} ({fields}) SELECT {cols} FROM {other_table_name} ON CONFLICT ({primary_key}) DO UPDATE SET {upsert_fields};"
        return sql.format(table_name=table_name, fields=fields, cols=cols, other_table_name=other_table_name, primary_key=primary_key, upsert_fields=upsert_fields)

    @classmethod
    def seed_or_update_self(self, **kwargs):
        logger.debug("Seeding/Updating {}", self.__name__)
        # Add records from both tables
        preforeclosure_table = ds.PSPreForeclosure
        preforeclosure_count = preforeclosure_table.objects.count()
        preforeclosure_cols = "concat({other_table_name}.indexno, {other_table_name}.bbl), {other_table_name}.bbl, {other_table_name}.indexno, {other_table_name}.address, {other_table_name}.documenttype, {other_table_name}.lientype, {other_table_name}.dateadded, {other_table_name}.creditor, {other_table_name}.debtor, {other_table_name}.mortgagedate, {other_table_name}.mortgageamount, NULL, {other_table_name}.key, \'PropertyShark\'".format(
            other_table_name=preforeclosure_table._meta.db_table, other_model_name=preforeclosure_table._meta.model_name)

        # foreclosure_table = ds.PSForeclosure
        # foreclosure_count = foreclosure_table.objects.count()
        # foreclosure_cols = "concat({other_table_name}.indexno, {other_table_name}.bbl), {other_table_name}.bbl, {other_table_name}.indexno, {other_table_name}.address, NULL, NULL, {other_table_name}.dateadded, NULL, NULL, NULL, NULL, {other_table_name}.auction, {other_table_name}.key, PropertyShark".format(
        #     nil={None}, other_table_name=foreclosure_table._meta.db_table, other_model_name=foreclosure_table._meta.model_name)

        kwargs['update'].total_rows = preforeclosure_count
        kwargs['update'].save()

        starting_count = self.objects.count()
        execute(self.upsert_permit_sql(preforeclosure_table, preforeclosure_cols))
        logger.debug("preforeclosure seeded - current count: {}", self.objects.count())
        rows_created_preforeclosure = self.objects.count() - starting_count
        kwargs['update'].rows_created = kwargs['update'].rows_created + rows_created_preforeclosure
        kwargs['update'].rows_updated = kwargs['update'].rows_updated + \
            (preforeclosure_count - rows_created_preforeclosure)
        kwargs['update'].save()
        logger.debug("Completed seed into {} for {}", self.__name__, preforeclosure_table._meta.db_table)

        # then update records with Foreclosure auction date
        #
        #
        #

        logger.debug('annotating properties for {}', self.__name__)
        # self.annotate_properties()

        dataset = self.get_dataset()
        dataset.api_last_updated = datetime.today()
        dataset.save()

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
