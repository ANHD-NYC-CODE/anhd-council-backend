from core import models as c_models
from core.utils.database import copy_file, write_gen_to_temp_file, create_gen_from_csv_diff, upsert_single_rows, batch_upsert_from_gen, bulk_insert_from_file, seed_from_csv_diff, from_csv_file_to_gen
from datasets import models as ds
from core.utils.typecast import Typecast
from django.core import files
from core.utils.transform import foreign_key_formatting
from django.conf import settings
from core.utils.csv_helpers import count_csv_rows, split_csv
import os
import csv
import requests
import tempfile
import re
import logging
import math
from dateutil.relativedelta import relativedelta
from django.db.models import Subquery, OuterRef, Count, IntegerField, F

from datetime import datetime, timezone

from core.tasks import async_seed_split_file

logger = logging.getLogger('app')


class BaseDatasetModel():
    @classmethod
    def get_dataset(self):
        return c_models.Dataset.objects.filter(model_name=self.__name__).first()

    @classmethod
    def download_file(self, endpoint):
        dataset = self.get_dataset()
        file_request = requests.get(endpoint, stream=True)
        # Was the request OK?
        if file_request.status_code != requests.codes.ok:
            # Nope, error handling, skip file etc etc etc
            logger.error("* ERROR * Download request failed: {}".format(endpoint))
            raise Exception("Request error: {}".format(file_request.status_code))

        # get filename
        if 'content-disposition' in file_request.headers:
            file_name = re.findall("filename=(.+)", file_request.headers['content-disposition'])[0]
        else:
            file_name = endpoint.split('/')[-1]

        # Create a temporary file
        lf = tempfile.NamedTemporaryFile()

        # Read the streamed file in sections
        downloaded = 0
        logger.info("Download started for: {} at {}".format(self.get_dataset().name, endpoint))

        for block in file_request.iter_content(1024 * 8):
            downloaded += len(block)
            logger.debug("{0} MB".format(downloaded / 1000000))
            # If no more file then stop
            if not block:
                break

            # Write file block to temporary file
            lf.write(block)
        data_file = c_models.DataFile(dataset=dataset)
        data_file.file.save(file_name, files.File(lf))
        logger.info("Download completed for: {} and saved to: {}".format(self.get_dataset().name, data_file.file.path))
        return data_file

    @classmethod
    def transform_self_from_file(self, file_path, update=None):
        return Typecast(self).cast_rows(self.transform_self(file_path, update))

    @classmethod
    def async_concurrent_seed(self, file_path, update=None):
        MAX_CONCURRENT_JOBS = 4
        csv_length = count_csv_rows(file_path)
        lines_per_csv = math.ceil(csv_length / MAX_CONCURRENT_JOBS)
        logger.debug("Splitting CSV into {}".format(MAX_CONCURRENT_JOBS))

        split_csvs = split_csv(file_path, settings.MEDIA_ROOT, self._meta.db_table, lines_per_csv)
        for csv_path in split_csvs:
            logger.debug('Creating job for split file {}'.format(csv_path))
            async_seed_split_file.delay(csv_path, update.id)

    @classmethod
    def seed_with_single(self, **kwargs):
        update = kwargs['update'] if 'update' in kwargs else None
        upsert_single_rows(self, self.transform_self_from_file(kwargs['file_path'], update=update), update=update)
        if 'delete_file' in kwargs and kwargs['delete_file']:
            os.remove(kwargs['file_path'])

    @classmethod
    def seed_or_update_with_filter(self, **kwargs):
        update = kwargs['update'] if 'update' in kwargs else None
        if self.objects.count() > 0:
            return upsert_single_rows(self, self.transform_self_from_file(kwargs['file_path'], update=update), update=update)
        else:
            return upsert_single_rows(self, self.transform_self_from_file(kwargs['file_path'], update=update), update=update)

    @classmethod
    def seed_with_upsert(self, **kwargs):
        update = kwargs['update'] if 'update' in kwargs else None
        return batch_upsert_from_gen(self, self.transform_self_from_file(kwargs['file_path'], update=update), settings.BATCH_SIZE, update=update)

    @classmethod
    # Good for overwrites
    def bulk_seed(self, **kwargs):
        if 'raw' in kwargs and kwargs['raw'] == True:
            copy_file(self, **kwargs)
        else:
            bulk_insert_from_file(self, **kwargs)

    @classmethod
    def seed_or_update_from_set_diff(self, **kwargs):

        new_file_path = kwargs['update'].file.file.path
        previous_file = kwargs['update'].previous_file
        update = kwargs['update'] if 'update' in kwargs else None

        if update:
            # count rows
            logger.debug('Counting csv rows...')
            count = -1  # offset for header
            for row in csv.reader(open(new_file_path, 'r')):
                count = count + 1
            update.total_rows = count
            update.save()

        if (previous_file and os.path.isfile(previous_file.file.path)):
            seed_from_csv_diff(previous_file.file.path, new_file_path, self, **kwargs)
        # if (previous_file and os.path.isfile(previous_file.file.path)):
        #     temp_file_path = write_gen_to_temp_file(create_gen_from_csv_diff(
        #         previous_file.file.path, new_file_path))
        #
        #     cleaned_diff_gen = self.transform_self(temp_file_path)
        #     logger.debug('Seeding diffed csv gen...')
        #     batch_upsert_from_gen(self, cleaned_diff_gen, settings.BATCH_SIZE, update=update)
        #     if os.path.isfile(temp_file_path):
        #         os.remove(temp_file_path)
        else:
            if 'single' in kwargs and kwargs['single']:
                self.seed_with_single(**kwargs)
            else:
                self.bulk_seed(**kwargs)

    @classmethod
    def annotate_all_properties_standard(self):
        logger.debug('annotating properties for: {}'.format(self.__name__))
        last30 = datetime.today().replace(tzinfo=timezone.utc) - relativedelta(days=30)
        lastyear = datetime.today().replace(tzinfo=timezone.utc) - relativedelta(years=1)
        last3years = datetime.today().replace(tzinfo=timezone.utc) - relativedelta(years=3)

        last30_subquery = Subquery(self.objects.filter(bbl=OuterRef('bbl'), **{self.QUERY_DATE_KEY + '__gte': last30}).values(
            self._meta.pk.name).annotate(count=Count(self._meta.pk.name)).values('count'))

        lastyear_subquery = Subquery(self.objects.filter(bbl=OuterRef(
            'bbl'), **{self.QUERY_DATE_KEY + '__gte': lastyear}).values(self._meta.pk.name).annotate(count=Count(self._meta.pk.name)).values('count'))

        last3years_subquery = Subquery(self.objects
                                       .filter(bbl=OuterRef('bbl'), **{self.QUERY_DATE_KEY + '__gte': last3years}).values(self._meta.pk.name)
                                       .annotate(count=Count(self._meta.pk.name))
                                       .values('count')
                                       )

        ds.PropertyAnnotation.objects.update(**{self.__name__.lower() + 's_last30': last30_subquery, self.__name__.lower(
        ) + 's_lastyear': lastyear_subquery, self.__name__.lower() + 's_last3years': last3years_subquery})

    @classmethod
    def annotate_property_standard(self, annotation):
        try:
            last30 = datetime.today().replace(tzinfo=timezone.utc) - relativedelta(days=30)
            lastyear = datetime.today().replace(tzinfo=timezone.utc) - relativedelta(years=1)
            last3years = datetime.today().replace(tzinfo=timezone.utc) - relativedelta(years=3)

            setattr(annotation, self.__name__.lower() + 's_last30', getattr(annotation.bbl,
                                                                            self.__name__.lower() + '_set').filter(**{self.QUERY_DATE_KEY + '__gte': last30}).count())

            setattr(annotation, self.__name__.lower() + 's_lastyear', getattr(annotation.bbl,
                                                                              self.__name__.lower() + '_set').filter(**{self.QUERY_DATE_KEY + '__gte': lastyear}).count())

            setattr(annotation, self.__name__.lower() + 's_last3years', getattr(annotation.bbl,
                                                                                self.__name__.lower() + '_set').filter(**{self.QUERY_DATE_KEY + '__gte': last3years}).count())

            return annotation
        except Exception as e:

            print(e)
            return

    @classmethod
    def annotate_all_properties_month_offset(self):
        last30 = datetime.today().replace(day=1, tzinfo=timezone.utc) - relativedelta(months=1)
        lastyear = datetime.today().replace(tzinfo=timezone.utc) - relativedelta(years=1)
        last3years = datetime.today().replace(tzinfo=timezone.utc) - relativedelta(years=3)

        last30_subquery = Subquery(self.objects.filter(bbl=OuterRef('bbl'), **{self.QUERY_DATE_KEY + '__gte': last30}).values('pk').annotate(
            cnt=Count('pk')).values('cnt'))

        lastyear_subquery = Subquery(self.objects.filter(bbl=OuterRef(
            'bbl'), **{self.QUERY_DATE_KEY + '__gte': lastyear}).values('pk').annotate(cnt=Count('pk')).values('cnt'))

        last3years_subquery = Subquery(self.objects
                                       .filter(bbl=OuterRef('bbl'), **{self.QUERY_DATE_KEY + '__gte': last3years}).values('pk')
                                       .annotate(cnt=Count('pk'))
                                       .values('cnt')
                                       )

        ds.PropertyAnnotation.objects.update(**{self.__name__.lower() + 's_last30': last30_subquery}, **{self.__name__.lower(
        ) + 's_lastyear': lastyear_subquery}, **{self.__name__.lower() + 's_last3years': last3years_subquery})

    @classmethod
    def annotate_property_month_offset(self, annotation):
        try:
            last30 = datetime.today().replace(day=1, tzinfo=timezone.utc) - relativedelta(months=1)
            lastyear = datetime.today().replace(tzinfo=timezone.utc) - relativedelta(years=1)
            last3years = datetime.today().replace(tzinfo=timezone.utc) - relativedelta(years=3)

            setattr(annotation, self.__name__.lower() + 's_last30', getattr(annotation.bbl,
                                                                            self.__name__.lower() + '_set').filter(**{self.QUERY_DATE_KEY + '__gte': last30}).count())

            setattr(annotation, self.__name__.lower() + 's_lastyear', getattr(annotation.bbl,
                                                                              self.__name__.lower() + '_set').filter(**{self.QUERY_DATE_KEY + '__gte': lastyear}).count())

            setattr(annotation, self.__name__.lower() + 's_last3years', getattr(annotation.bbl,
                                                                                self.__name__.lower() + '_set').filter(**{self.QUERY_DATE_KEY + '__gte': last3years}).count())

            return annotation
        except Exception as e:

            print(e)
            return
