from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_xlsx_file_to_gen
from datasets import models as ds
from core.tasks import async_download_and_update

import logging
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
    auction = models.DateField(blank=True, null=True)  # auction
    auctiontime = models.TextField(blank=True, null=True)
    auctionlocation = models.TextField(blank=True, null=True)
    # maybe only add if blank?
    dateadded = models.DateField(blank=True, null=True)
    plaintiff = models.TextField(blank=True, null=True)
    defendant = models.TextField(blank=True, null=True)
    lien = models.TextField(blank=True, null=True)
    # justgment IS A DATETIME FIELD!
    judgment = models.TextField(blank=True, null=True)
    referee = models.TextField(blank=True, null=True)
    plaintiffsattorney = models.TextField(blank=True, null=True)
    foreclosuretype = models.TextField(blank=True, null=True)
    legalprocess = models.TextField(blank=True, null=True)
    hasphoto = models.TextField(blank=True, null=True)
    unitnumber = models.TextField(blank=True, null=True)

    @classmethod
    def create_async_update_worker(self, endpoint=None, file_name=None):
        async_download_and_update.delay(
            self.get_dataset().id, endpoint=endpoint, file_name=file_name)

    @classmethod
    def download(self, endpoint=None, file_name=None):
        return self.download_file(endpoint, file_name=file_name, ps_requests=True)

    @classmethod
    def pre_validation_filters(self, gen_rows):
        for row in gen_rows:
            row['bbl'] = ''.join(row['bbl'].split('-')[0:3])
            row['key'] = "#{}-#{}".format(row['indexno'], row['bbl'])
            yield row

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(from_xlsx_file_to_gen(file_path, 'Foreclosure Auctions Details', update, skip_rows=7))

    @classmethod
    def update_foreclosure_auction_dates(self, **kwargs):
        updated_foreclosures = []
        gen_rows = self.transform_self_from_file(kwargs['file_path'])
        for row in gen_rows:
            try:
                foreclosure = ds.Foreclosure.objects.get(
                    index=row['indexno'], bbl=row['bbl'])
                foreclosure.auction = row['auction']
                updated_foreclosures.append(foreclosure)
            except Exception as e:
                pass

        ds.Foreclosure.objects.bulk_update(updated_foreclosures, ['auction'])

    @classmethod
    def seed_or_update_self(self, **kwargs):
        logger.info("Seeding/Updating {}", self.__name__)
        self.seed_with_upsert(**kwargs)
        self.update_foreclosure_auction_dates(**kwargs)
