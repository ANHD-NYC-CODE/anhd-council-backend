from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null
import logging

logger = logging.getLogger('app')


class Eviction(BaseDatasetModel, models.Model):
    download_endpoint = "https://data.cityofnewyork.us/resource/fxkt-ewig.csv"
    # "borough"
    "court_index_number"
    "docket_number"
    "eviction_address"
    "eviction_apt_num"
    "eviction_zip"
    "executed_date"
    "marshal_first_name"
    "marshal_last_name"
    "residential_commercial_ind"
    "schedule_status"

    courtindexnumber = models.TextField(primary_key=True, blank=False, null=False)
    bbl = models.ForeignKey('Property', db_column='bbl', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=False)
    boro = models.TextField(blank=True, null=True)
    docketnumber = models.TextField(blank=True, null=True)
    evictionaddress = models.TextField(blank=True, null=True)
    evictionaptnum = models.TextField(blank=True, null=True)
    evictionzip = models.TextField(blank=True, null=True)
    uniqueid = models.TextField(blank=True, null=True)
    executeddate = models.DateTimeField(db_index=True, blank=True, null=True)
    marshalfirstname = models.TextField(blank=True, null=True)
    marshallastname = models.TextField(blank=True, null=True)
    residentialcommercialind = models.TextField(db_index=True, blank=True, null=True)
    scheduledstatus = models.TextField(db_index=True, blank=True, null=True)
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
            if is_null(row['courtindex']):
                continue
            yield row

    # trims down new update files to preserve memory
    # uses original header values
    @classmethod
    def update_set_filter(self, csv_reader, headers):
        return csv_reader

    # Because the CSV has commas in marshalllastname column - Smith,jr.
    @classmethod
    def clean_evictions_csv(self, gen_rows):
        for row in gen_rows:
            row = row.lower().replace(',jr.', ' jr')
            row = row.lower().replace(', jr.', ' jr')
            row = row.lower().replace("STREE T", 'STREET')
            row = row.lower().replace("STR EET", 'STREET')
            row = row.lower().replace("ST REET", 'STREET')
            row = row.lower().replace("STRE ET", 'STREET')
            row = row.lower().replace("S TREET", 'STREET')
            # ROAD
            row = row.lower().replace("ROA D", 'ROAD')
            row = row.lower().replace("RO AD", 'ROAD')
            row = row.lower().replace("R OAD", 'ROAD')
            # AVENUE
            row = row.lower().replace("AVENU E", 'AVENUE')
            row = row.lower().replace("AVEN UE", 'AVENUE')
            row = row.lower().replace("AVE NUE", 'AVENUE')
            row = row.lower().replace("AV ENUE", 'AVENUE')
            row = row.lower().replace("A VENUE", 'AVENUE')
            row = row.lower().replace("AVNUE", 'AVENUE')
            # PARKWAY
            row = row.lower().replace("P ARKWAY", 'PARKWAY')
            row = row.lower().replace("PA RKWAY", 'PARKWAY')
            row = row.lower().replace("PAR KWAY", 'PARKWAY')
            row = row.lower().replace("PARK WAY", 'PARKWAY')
            row = row.lower().replace("PARKWA Y", 'PARKWAY')
            row = row.lower().replace("PARKWA", 'PARKWAY')
            # HIGHWAY
            row = row.lower().replace("HWY", 'HIGHWAY')
            # NORTH
            row = row.lower().replace("N ORTH", 'NORTH')
            row = row.lower().replace("NOR TH", 'NORTH')
            # SOUTH
            row = row.lower().replace("SOUT H", 'SOUTH')
            row = row.lower().replace("S OUTH", 'SOUTH')
            row = row.lower().replace("SOU TH", 'SOUTH')
            # BOULEVARD
            row = row.lower().replace("BOULEVAR D", 'BOULEVARD')
            row = row.lower().replace("BOULEVA RD", 'BOULEVARD')
            row = row.lower().replace("BOULEV ARD", 'BOULEVARD')
            row = row.lower().replace("BOULE VARD", 'BOULEVARD')
            row = row.lower().replace("BOUL EVARD", 'BOULEVARD')
            row = row.lower().replace("BOU LEVARD", 'BOULEVARD')
            row = row.lower().replace("B OULEVARD", 'BOULEVARD')
            # BLVD
            row = row.lower().replace("BLVD", 'BLVD')
            row = row.lower().replace("BLV D", 'BLVD')
            row = row.lower().replace("BL VD", 'BLVD')
            row = row.lower().replace("B LVD", 'BLVD')
            # remove double space
            row = row.lower().replace("  ", " ")
            row = row.lower().replace("   ", " ")
            # rmove +
            row = row.lower().replace("+", '')
            # remove all periods
            row = row.lower().replace('.', '')
            yield row

    @classmethod
    def link_eviction_to_pluto_by_address(self):
        evictions = self.objects.all()
        for eviction in evictions:
            pattern = r'\d*.*?(LANE|EXPRESSWAY|PARKWAY|STREET|AVENUE|PLACE|BOULEVARD|DRIVE)'
            import pdb
            pdb.set_trace()

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(from_csv_file_to_gen(file_path, update, self.clean_evictions_csv))

    @classmethod
    def seed_or_update_self(self, **kwargs):
        logger.debug("Seeding/Updating {}", self.__name__)
        update = self.seed_or_update_from_set_diff(**kwargs)
        self.link_eviction_to_pluto_by_address()
        return update

    def __str__(self):
        return str(self.violationid)
