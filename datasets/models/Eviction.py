from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null
from datasets import models as ds
from core.utils.bbl import boro_to_abrv

import re
import logging

logger = logging.getLogger('app')


class Eviction(BaseDatasetModel, models.Model):
    download_endpoint = "https://data.cityofnewyork.us/resource/fxkt-ewig.csv"
    # download_endpoint = "https://data.cityofnewyork.us/api/views/6z8x-wfk4/rows.csv?accessType=DOWNLOAD"

    courtindexnumbernumber = models.TextField(primary_key=True, blank=False, null=False)
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
            row = row.upper().replace("STREE T", 'STREET')
            row = row.upper().replace("STR EET", 'STREET')
            row = row.upper().replace("ST REET", 'STREET')
            row = row.upper().replace("STRE ET", 'STREET')
            row = row.upper().replace("S TREET", 'STREET')
            # ROAD
            row = row.upper().replace("ROA D", 'ROAD')
            row = row.upper().replace("RO AD", 'ROAD')
            row = row.upper().replace("R OAD", 'ROAD')

            # ROAD
            row = row.upper().replace("ROA D", 'ROAD')
            row = row.upper().replace("RO AD", 'ROAD')
            row = row.upper().replace("R OAD", 'ROAD')
            # AVENUE
            row = row.upper().replace("AVENU E", 'AVENUE')
            row = row.upper().replace("AVEN UE", 'AVENUE')
            row = row.upper().replace("AVE NUE", 'AVENUE')
            row = row.upper().replace("AV ENUE", 'AVENUE')
            row = row.upper().replace("A VENUE", 'AVENUE')
            row = row.upper().replace("AVNUE", 'AVENUE')
            # PARKWAY
            row = row.upper().replace("P ARKWAY", 'PARKWAY')
            row = row.upper().replace("PA RKWAY", 'PARKWAY')
            row = row.upper().replace("PAR KWAY", 'PARKWAY')
            row = row.upper().replace("PARK WAY", 'PARKWAY')
            row = row.upper().replace("PARKWA Y", 'PARKWAY')
            row = row.upper().replace("PARKWA", 'PARKWAY')
            row = row.upper().replace("PARKWAYY", 'PARKWAY')

            # HIGHWAY
            row = row.upper().replace("HWY", 'HIGHWAY')
            # NORTH
            row = row.upper().replace("N ORTH", 'NORTH')
            row = row.upper().replace("NOR TH", 'NORTH')
            # SOUTH
            row = row.upper().replace("SOUT H", 'SOUTH')
            row = row.upper().replace("S OUTH", 'SOUTH')
            row = row.upper().replace("SOU TH", 'SOUTH')
            # BOULEVARD
            row = row.upper().replace("BOULEVAR D", 'BOULEVARD')
            row = row.upper().replace("BOULEVA RD", 'BOULEVARD')
            row = row.upper().replace("BOULEV ARD", 'BOULEVARD')
            row = row.upper().replace("BOULE VARD", 'BOULEVARD')
            row = row.upper().replace("BOUL EVARD", 'BOULEVARD')
            row = row.upper().replace("BOU LEVARD", 'BOULEVARD')
            row = row.upper().replace("B OULEVARD", 'BOULEVARD')
            # BLVD
            row = row.upper().replace("BLVD", 'BLVD')
            row = row.upper().replace("BLV D", 'BLVD')
            row = row.upper().replace("BL VD", 'BLVD')
            row = row.upper().replace("B LVD", 'BLVD')

            # TERRACE
            row = row.upper().replace("TERRAC E", 'TERRACE')
            row = row.upper().replace("TERRA CE", 'TERRACE')
            row = row.upper().replace("TERR ACE", 'TERRACE')
            row = row.upper().replace("TER RACE", 'TERRACE')
            row = row.upper().replace("TE RRACE", 'TERRACE')
            row = row.upper().replace("T ERRACE", 'TERRACE')

            # remove double space
            row = row.upper().replace("  ", " ")
            row = row.upper().replace("   ", " ")
            # rmove +
            row = row.upper().replace("+", '')
            # remove all periods
            row = row.upper().replace('.', '')

            # Remove Street Suffixes
            pattern = re.compile(r"([0-9]+)(TH|ND|ST|RD)")
            row = re.sub(pattern, r"\1", row)

            # Replace Street Appreviations
            HOLY_SAINTS = ['JOSEPH', 'MARKS', 'LAWRENCE', 'JAMES',
                           'NICHOLAS', 'HOLLIS', 'JOHNS', "JOHN's"]

            row = re.sub(r"\bLN\b", "LANE", row)
            row = re.sub(r"\bPL\b", "PLACE", row)
            row = re.sub(r"\bDR\b", "DRIVE", row)
            row = re.sub(r"\bRD\b", "ROAD", row)
            row = re.sub(r"\bAVE\b", "AVENUE", row)
            row = re.sub(r"\bBLVD\b", "BOULEVARD", row)
            row = re.sub(r"\bBDWAY\b", "BROADWAY", row)
            row = re.sub(r"\bPKWY\b", "PARKWAY", row)
            row = re.sub(r"\bPKWAY\b", "PARKWAY", row)
            row = re.sub(r"(?!{})(?=\bST\b)(\bST\b)".format(
                ".*" + saint + "|" for saint in HOLY_SAINTS), "STREET", row)

            # Replace Compass appreviations

            row = re.sub(r"\bN\b", "NORTH", row)
            row = re.sub(r"\bE\b", "EAST", row)
            row = re.sub(r"\bS\b", "SOUTH", row)
            row = re.sub(r"\bW\b", "WEST", row)

            yield row.upper().strip()

    @classmethod
    def link_eviction_to_pluto_by_address(self):
        evictions = self.objects.filter(bbl__isnull=True)
        for eviction in evictions:
            pattern = r'[0-9].*?(LANE|EXPRESSWAY|PARKWAY|STREET|AVENUE|PLACE|BOULEVARD|DRIVE|ROAD|CONCOURSE|PLAZA|TERRACE)'
            match = re.search(pattern, eviction.evictionaddress)
            if match:
                address = match.group(0)
                property_match = ds.Property.objects.filter(
                    zipcode=eviction.evictionzip, address=address).first()
                if property_match:
                    eviction.bbl = property_match
                    eviction.save()
                else:
                    print("no property match: {}".format(address))

            else:
                print("no match: {}".format(eviction.evictionaddress))

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
        return str(self.courtindexnumbernumber)
