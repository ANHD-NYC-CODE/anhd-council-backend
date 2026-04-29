from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null, is_older_than, does_not_contain_values
import logging
from core.tasks import async_download_and_update


logger = logging.getLogger('app')

# TODO - generate unique key during transform and add as a model field
# remove unqiue constraints beacuse it's slowing down updates a lot

# Update process: Automatic
# Update strategy: Overwrite
#


class DOBPermitIssuedNow(BaseDatasetModel, models.Model):
    API_ID = 'rbx6-tga4'
    base_download_endpoint = "https://data.cityofnewyork.us/resource/rbx6-tga4.csv"

    jobfilingnumber = models.TextField(blank=True, null=True)
    workpermit = models.TextField(blank=True, null=True)
    bin = models.ForeignKey('Building', db_column='bin', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=True)
    bbl = models.ForeignKey('Property', db_column='bbl', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=False)
    filingreason = models.TextField(blank=True, null=True)
    houseno = models.TextField(blank=True, null=True)
    streetname = models.TextField(blank=True, null=True)
    borough = models.TextField(blank=True, null=True)
    lot = models.IntegerField(blank=True, null=True)
    block = models.IntegerField(blank=True, null=True)
    cbno = models.TextField(blank=True, null=True)
    aptcondonos = models.TextField(blank=True, null=True)
    workonfloor = models.TextField(blank=True, null=True)
    worktype = models.TextField(blank=True, null=True)
    permitteeslicensetype = models.TextField(blank=True, null=True)
    applicantlicense = models.TextField(blank=True, null=True)
    applicantfirstname = models.TextField(blank=True, null=True)
    applicantmiddlename = models.TextField(blank=True, null=True)
    applicantlastname = models.TextField(blank=True, null=True)
    applicantbusinessname = models.TextField(blank=True, null=True)
    applicantbusinessaddress = models.TextField(blank=True, null=True)
    filingrepresentativefirstname = models.TextField(blank=True, null=True)
    filingrepresentativemiddleinitial = models.TextField(blank=True, null=True)
    filingrepresentativelastname = models.TextField(blank=True, null=True)
    filingrepresentativebusinessname = models.TextField(blank=True, null=True)
    approveddate = models.DateField(blank=True, null=True)
    issueddate = models.DateField(blank=True, null=True)
    expireddate = models.DateField(blank=True, null=True)
    jobdescription = models.TextField(blank=True, null=True)
    estimatedjobcosts = models.TextField(blank=True, null=True)
    ownerbusinessname = models.TextField(blank=True, null=True)
    ownername = models.TextField(blank=True, null=True)
    ownerstreetaddress = models.TextField(blank=True, null=True)
    ownercity = models.TextField(blank=True, null=True)
    ownerstate = models.TextField(blank=True, null=True)
    ownerzipcode = models.TextField(blank=True, null=True)

    # class Meta:
    #     unique_together = ('jobfilingnumber', 'workpermit', 'issueddate')

    @classmethod
    def create_async_update_worker(self, endpoint=None, file_name=None):
        async_download_and_update.delay(
            self.get_dataset().id, endpoint=endpoint, file_name=file_name)

    @classmethod
    def download(self, endpoint=None, file_name=None):
        # Fields based on DOBIssuedPermit usage
        fields = [
            "job_filing_number",  # jobfilingnumber
            "work_permit",        # workpermit
            "bin",               # bin
            "borough",           # borough
            "house_no",          # houseno
            "street_name",       # streetname
            "lot",              # lot
            "block",            # block
            "work_type",         # worktype
            "job_description",   # jobdescription
            "issued_date",       # issueddate
            "expired_date",      # expireddate
            "filing_reason"      # filingreason
        ]
        download_url = f"{self.base_download_endpoint}?$select={','.join(fields)}&$limit=100000000"
    
        logger.info("Downloading DOB Permit Issued Now filtered dataset from: %s", download_url)
        return self.download_file(download_url, file_name=file_name or "DOBPermitIssuedNow")

    @classmethod
    def clean_null_bytes_headers(cls, gen_rows):
        try:
            header_row = next(gen_rows)
            logger.info("Processing header row: %s", header_row)
        except StopIteration:
            logger.error("Empty CSV generator received")
            raise ValueError("The CSV file is empty or invalid")
    
        # Clean BOM and strip ID
        cleaned_header = {key.lstrip('\ufeff'): value for key, value in header_row.items() if key != "id"}
        logger.debug("Cleaned header row (ID removed if present): %s", cleaned_header)
    
        # Header replacements for Socrata resource API snake_case → camelCase
        socrata_replacements = {
            "job_filing_number": "jobfilingnumber",
            "work_permit": "workpermit",
            "bin": "bin",
            "borough": "borough",
            "house_no": "houseno",
            "street_name": "streetname",
            "lot": "lot",
            "block": "block",
            "work_type": "worktype",
            "job_description": "jobdescription",
            "issued_date": "issueddate",
            "expired_date": "expireddate",
            "filing_reason": "filingreason"
        }
    
        # Apply replacements to keys
        remapped_header = {}
        for key, value in cleaned_header.items():
            new_key = socrata_replacements.get(key, key)
            remapped_header[new_key] = value
    
        logger.info("Remapped Header Row: %s", remapped_header)
    
        yield remapped_header
    
        # Process remaining rows
        for row in gen_rows:
            if isinstance(row, dict):
                if "id" in row:
                    del row["id"]
                    logger.debug("Removed 'id' from row: %s", row)
    
                for key, value in row.items():
                    if isinstance(value, str):
                        row[key] = value.replace("\0", "").replace("\t", ",")
    
                yield row
    
            elif isinstance(row, str):
                row = row.replace("\0", "").replace("\t", ",")
                yield row
    
            else:
                logger.warning("Unexpected row type: %s", type(row))
                yield row

    @classmethod
    def pre_validation_filters(self, gen_rows):
        for row in gen_rows:
            if is_null(row['jobfilingnumber']) or is_null(row['workpermit']) or is_null(row['issueddate']):
                continue
            yield row

    # trims down new update files to preserve memory
    # uses original header values
    @classmethod
    def update_set_filter(self, csv_reader, headers):
        for row in csv_reader:
            if headers.index('Issued Date') and is_older_than(row[headers.index('Issued Date')], 1):
                continue
            yield row

    @classmethod
    def transform_self(self, file_path, update=None):
        rows = from_csv_file_to_gen(file_path, update)
        cleaned_rows = self.clean_null_bytes_headers(rows)
        return self.pre_validation_filters(with_bbl(cleaned_rows))

    @classmethod
    def seed_or_update_self(self, **kwargs):
        logger.info("Seeding/Updating %s", self.__name__)
        return self.bulk_seed(**kwargs, overwrite=True)

    def __str__(self):
        return str(self.jobfilingnumber)
