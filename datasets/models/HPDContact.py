from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null
import logging
from core.tasks import async_download_and_update


logger = logging.getLogger('app')


class HPDContact(BaseDatasetModel, models.Model):
    API_ID = 'feu5-w2e2'
    download_endpoint = "https://data.cityofnewyork.us/api/views/feu5-w2e2/rows.csv?accessType=DOWNLOAD"

    registrationcontactid = models.IntegerField(primary_key=True, blank=False, null=False)
    registrationid = models.ForeignKey('HPDRegistration', db_column='registrationid', db_constraint=False,
                                       on_delete=models.SET_NULL, null=True, blank=False)
    type = models.TextField(blank=True, null=True)
    contactdescription = models.TextField(blank=True, null=True)
    corporationname = models.TextField(blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    firstname = models.TextField(blank=True, null=True)
    middleinitial = models.TextField(blank=True, null=True)
    lastname = models.TextField(blank=True, null=True)
    businesshousenumber = models.TextField(blank=True, null=True)
    businessstreetname = models.TextField(blank=True, null=True)
    businessapartment = models.TextField(blank=True, null=True)
    businesscity = models.TextField(blank=True, null=True)
    businessstate = models.TextField(blank=True, null=True)
    businesszip = models.TextField(blank=True, null=True)

    @classmethod
    def create_async_update_worker(self, endpoint=None, file_name=None):
        async_download_and_update.delay(self.get_dataset().id, endpoint=endpoint, file_name=file_name)

    @classmethod
    def download(self, endpoint=None, file_name=None):
        return self.download_file(self.download_endpoint, file_name=file_name)

    @classmethod
    def pre_validation_filters(self, gen_rows):
        for row in gen_rows:
            if is_null(row['registrationcontactid']):
                continue
            yield row

    # trims down new update files to preserve memory
    # uses original header values
    @classmethod
    def update_set_filter(self, csv_reader, headers):
        return csv_reader

    # adding code to remove any entries not present in the new dataset being downloaded. It will use the registrationcontactid (it assumes each is unique.) 
    @classmethod
    def remove_outdated_entries(cls, new_entry_ids):
        cls.objects.exclude(registrationcontactid__in=new_entry_ids).delete()

    
    # When you sync/download the data from the API and call this updated transform_self, it will remove any entries from the HPDContact table that are not present in the new data.
    @classmethod
    def transform_self(cls, file_path, update=None):
        new_entry_ids = set()
        for row in cls.pre_validation_filters(with_bbl(from_csv_file_to_gen(file_path, update), allow_blank=True)):
            new_entry_ids.add(row['registrationcontactid'])
            yield row
        cls.remove_outdated_entries(new_entry_ids)


    @classmethod
    def seed_or_update_self(self, **kwargs):
        self.seed_with_upsert(**kwargs)


    def __str__(self):
        return str(self.registrationcontactid)
