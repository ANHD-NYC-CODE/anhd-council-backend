from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null
from datasets import models as ds
from core.utils.bbl import boro_to_abrv
from core.utils.address import clean_number_and_streets

import re
import logging

logger = logging.getLogger('app')


class Eviction(BaseDatasetModel, models.Model):
    download_endpoint = "https://data.cityofnewyork.us/api/views/6z8x-wfk4/rows.csv?accessType=DOWNLOAD"

    courtindexnumber = models.TextField(primary_key=True, blank=False, null=False)
    bbl = models.ForeignKey('Property', db_column='bbl', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=True)
    borough = models.TextField(blank=True, null=True)
    docketnumber = models.TextField(blank=True, null=True)
    evictionaddress = models.TextField(blank=True, null=True)
    evictionaptnum = models.TextField(blank=True, null=True)
    evictionzip = models.TextField(blank=True, null=True)
    uniqueid = models.TextField(blank=True, null=True)
    executeddate = models.DateTimeField(db_index=True, blank=True, null=True)
    marshalfirstname = models.TextField(blank=True, null=True)
    marshallastname = models.TextField(blank=True, null=True)
    residentialcommercialind = models.TextField(db_index=True, blank=True, null=True)
    schedulestatus = models.TextField(db_index=True, blank=True, null=True)
    # cleanedaddress1 = models.TextField(blank=True, null=True)
    # cleanedaddress2 = models.TextField(blank=True, null=True)
    # lat = models.DecimalField(decimal_places=8, max_digits=16, blank=True, null=True)
    # lng = models.DecimalField(decimal_places=8, max_digits=16, blank=True, null=True)
    # geocoder = models.TextField(blank=True, null=True)

    @classmethod
    def download(self):
        return self.download_file(self.download_endpoint)

    @classmethod
    def pre_validation_filters(self, gen_rows):
        for row in gen_rows:
            if is_null(row['courtindexnumber']):
                continue
            yield row

    # trims down new update files to preserve memory
    # uses original header values
    @classmethod
    def update_set_filter(self, csv_reader, headers):
        return csv_reader


# from core.models import DataFile, Update;file_path = DataFile.objects.last().file.path;update = Update.objects.last();update.dataset.seed_dataset(file_path=file_path, update=update)

# Because the CSV has commas in marshalllastname column - Smith,jr.


    @classmethod
    def clean_evictions_csv(self, gen_rows):
        for row in gen_rows:
            row = row.upper()
            row = row.upper().replace(',JR.', ' JR')
            row = row.upper().replace(', JR.', ' JR')

            row = clean_number_and_streets(row, True)
            yield row.upper().strip()

    @classmethod
    def link_eviction_to_pluto_by_address(self):
        def search_property_address(eviction, address):
            match = ds.Property.objects.filter(address__icontains=address)
            if len(match) == 1:
                eviction.bbl = match[0]
                eviction.save()
            elif len(match) > 1:
                if not re.match(r"(\d+ (STREET|AVENUE))", address):
                    eviction.bbl = match[0]
                    eviction.save()
                else:
                    logger.debug("Unable to choose from multiple property matches: {}".format(address))
            else:
                logger.debug("No property match found: {}".format(address))

        evictions = self.objects.filter(bbl__isnull=True)
        for eviction in evictions:
            pattern = r'[0-9].*?(LANE|EXPRESSWAY|PARKWAY|STREET|(AVENUE \w\b|AVENUE)|PLACE|BOULEVARD|DRIVE|ROAD|CONCOURSE|PLAZA|TERRACE|COURT|LOOP|CRESENT|BROADWAY|WAY|WALK|TURNPIKE|PROMENADE|RIDGE|OVAL|SLIP|CIRCLE)'
            match = re.search(pattern, eviction.evictionaddress)
            if match:
                address = match.group(0)
                address_match = ds.AddressRecord.objects.filter(address=address + ' {}'.format(eviction.borough))
                if len(address_match) == 1:
                    eviction.bbl = address_match[0].bbl
                    eviction.save()
                elif len(address_match) > 1:
                    # not a super generic query like 123 STREET or 45 AVENUE
                    if not re.match(r"(\d+ (STREET|AVENUE))", address):
                        eviction.bbl = address_match[0].bbl
                        eviction.save()
                    else:
                        search_property_address(eviction, address)
                else:
                    search_property_address(eviction, address)

            else:
                logger.debug("no match: {}".format(eviction.evictionaddress))

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(from_csv_file_to_gen(file_path, update, self.clean_evictions_csv))

    @classmethod
    def seed_or_update_self(self, **kwargs):
        logger.debug("Seeding/Updating {}", self.__name__)
        update = self.seed_with_upsert(**kwargs)
        self.link_eviction_to_pluto_by_address()
        return update

    def __str__(self):
        return str(self.courtindexnumber)
