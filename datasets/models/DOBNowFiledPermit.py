from django.db import models
from django.db import connection
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null, is_older_than, does_not_contain_values
from datetime import datetime
import logging
from core.tasks import async_download_and_update

logger = logging.getLogger('app')

def transform_date(value):
    """Convert 'MM/DD/YYYY HH:MM:SS AM/PM' or 'MM/DD/YYYY' to 'YYYY-MM-DD'."""
    if isinstance(value, str) and value.strip():
        try:
            return datetime.strptime(value, "%m/%d/%Y %I:%M:%S %p").date()
        except ValueError:
            try:
                return datetime.strptime(value, "%m/%d/%Y").date()
            except ValueError:
                return None  # Return None if format is invalid
    return None  # Return None for empty values


class DOBNowFiledPermit(BaseDatasetModel, models.Model):
    # download_endpoint = "https://data.cityofnewyork.us/api/views/w9ak-ipjd/rows.csv?accessType=DOWNLOAD"
    download_endpoint = "  https://anhd2402.bpbuild.com/test.csv?accessType=DOWNLOAD"

  
    API_ID = 'w9ak-ipjd'

    class Meta:
        indexes = [
            # models.Index(fields=['bbl', 'dobrundate']),
            # models.Index(fields=['dobrundate', 'bbl']),
            # models.Index(fields=['bbl', 'prefilingdate']),
            # models.Index(fields=['prefilingdate', 'bbl']),
        ]

    jobfilingnumber = models.TextField(blank=False, null=False)
    bbl = models.ForeignKey('Property', db_column='bbl', db_constraint=False, 
                            on_delete=models.SET_NULL, null=True, blank=False)
    bin = models.ForeignKey('Building', db_column='bin', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=True)
    filingstatus = models.TextField(blank=True, null=True)
    houseno = models.TextField(blank=True, null=True)
    streetname = models.TextField(blank=True, null=True)
    borough = models.TextField(blank=True, null=True)
    block = models.TextField(blank=True, null=True)
    lot = models.TextField(blank=True, null=True)
    commmunityboard = models.TextField(blank=True, null=True)
    workonfloor = models.TextField(blank=True, null=True)
    aptcondonos = models.TextField(blank=True, null=True)
    applicantprofessionaltitle = models.TextField(blank=True, null=True)
    applicantlicense = models.TextField(blank=True, null=True)
    applicantfirstname = models.TextField(blank=True, null=True)
    applicantsmiddleinitial = models.TextField(blank=True, null=True)
    applicantlastname = models.TextField(blank=True, null=True)
    ownersbusinessname = models.TextField(blank=True, null=True)
    ownersstreetname = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    zip = models.TextField(blank=True, null=True)
    filingrepresentativefirstname = models.TextField(blank=True, null=True)
    filingrepresentativemiddleinitial = models.TextField(blank=True, null=True)
    filingrepresentativelastname = models.TextField(blank=True, null=True)
    filingrepresentativebusinessname = models.TextField(blank=True, null=True)
    filingrepresentativestreetname = models.TextField(blank=True, null=True)
    filingrepresentativecity = models.TextField(blank=True, null=True)
    filingrepresentativestate = models.TextField(blank=True, null=True)
    filingrepresentativezip = models.TextField(blank=True, null=True)
    sprinklerworktype = models.BooleanField(blank=True, null=True)
    plumbingworktype = models.BooleanField(blank=True, null=True)
    initialcost = models.IntegerField(blank=True, null=True)
    totalconstructionfloorarea = models.IntegerField(blank=True, null=True)
    reviewbuildingcode = models.IntegerField(blank=True, null=True)
    littlee = models.BooleanField(blank=True, null=True)
    unmappedccostreet = models.BooleanField(blank=True, null=True)
    requestlegalization = models.BooleanField(blank=True, null=True)
    includespermanentremoval = models.BooleanField(blank=True, null=True)
    incompliancewithnycecc = models.BooleanField(blank=True, null=True)
    exemptfromnycecc = models.BooleanField(blank=True, null=True)
    buildingtype = models.TextField(blank=True, null=True)
    existingstories = models.IntegerField(blank=True, null=True)
    existingheight = models.IntegerField(blank=True, null=True)
    existingdwellingunits = models.IntegerField(blank=True, null=True)
    proposednoofstories = models.IntegerField(blank=True, null=True)
    proposedheight = models.IntegerField(blank=True, null=True)
    proposeddwellingunits = models.IntegerField(blank=True, null=True)
    specialinspectionrequirement = models.TextField(blank=True, null=True)
    specialinspectionagencynumber = models.TextField(blank=True, null=True)
    progressinspectionrequirement = models.TextField(blank=True, null=True)
    built1informationvalue = models.TextField(blank=True, null=True)
    built2informationvalue = models.TextField(blank=True, null=True)
    built2ainformationvalue = models.TextField(blank=True, null=True)
    built2binformationvalue = models.TextField(blank=True, null=True)
    standpipe = models.BooleanField(blank=True, null=True)
    antenna = models.BooleanField(blank=True, null=True)
    curbcut = models.BooleanField(blank=True, null=True)
    sign = models.BooleanField(blank=True, null=True)
    fence = models.BooleanField(blank=True, null=True)
    scaffold = models.BooleanField(blank=True, null=True)
    shed = models.BooleanField(blank=True, null=True)
    latitude = models.DecimalField(
        decimal_places=16, max_digits=32, blank=True, null=True)
    longitude = models.DecimalField(
        decimal_places=16, max_digits=32, blank=True, null=True)
    councildistrict = models.TextField(blank=True, null=True)
    censustract = models.TextField(blank=True, null=True)
    nta = models.TextField(blank=True, null=True)
    bin_2 = models.TextField(blank=True, null=True)
    currentstatusdate = models.DateField(blank=True, null=True)
    filingdate = models.DateField(blank=True, null=True)
    firstpermitdate = models.DateField(blank=True, null=True)
    permitissuedate = models.DateField(blank=True, null=True)
    boilerequipmentworktype = models.BooleanField(blank=True, null=True)
    earthworkworktype = models.BooleanField(blank=True, null=True)
    foundationworktype = models.BooleanField(blank=True, null=True)
    generalconstructionworktype = models.BooleanField(blank=True, null=True)
    mechanicalsystemsworktype = models.BooleanField(blank=True, null=True)
    placeofassemblyworktype = models.BooleanField(blank=True, null=True)
    protectionmechanicalmethodsworktype = models.BooleanField(blank=True, null=True)
    sidewalkshedworktype = models.BooleanField(blank=True, null=True)
    structuralworktype = models.BooleanField(blank=True, null=True)
    supportofexcavationworktype = models.BooleanField(blank=True, null=True)
    temporaryplaceofassemblyworktype = models.BooleanField(blank=True, null=True)
    jobtype = models.TextField(blank=True, null=True)
    ownerscity = models.TextField(blank=True, null=True)
    ownersstate = models.TextField(blank=True, null=True)
    ownerszip = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        def convert_boolean(value):
            """Convert Yes/No strings to True/False without changing DB storage."""
            if isinstance(value, str):
                value = value.strip().lower()
                if value == "yes":
                    return True
                elif value == "no":
                    return False
            return value  # Return as-is if it's already True/False or None
    
        # Always overwrite city, state, and zip with owners* values
        self.city = self.ownerscity
        self.state = self.ownersstate
        self.zip = self.ownerszip
        self.permitissuedate = self.firstpermitdate  # Always overwrite permitissuedate
    
        # ✅ Convert Boolean fields
        boolean_fields = [
            "sprinklerworktype", "plumbingworktype", "littlee", "unmappedccostreet",
            "requestlegalization", "includespermanentremoval", "incompliancewithnycecc",
            "exemptfromnycecc", "standpipe", "antenna", "curbcut", "sign", "fence",
            "scaffold", "shed", "boilerequipmentworktype", "earthworkworktype",
            "foundationworktype", "generalconstructionworktype",
            "mechanicalsystemsworktype", "placeofassemblyworktype",
            "protectionmechanicalmethodsworktype", "sidewalkshedworktype",
            "structuralworktype", "supportofexcavationworktype",
            "temporaryplaceofassemblyworktype"
        ]
    
        for field in boolean_fields:
            setattr(self, field, convert_boolean(getattr(self, field)))
    
        # ✅ Convert empty string numeric fields to None
        numeric_fields = [
            "initialcost", "totalconstructionfloorarea", "reviewbuildingcode",
            "existingstories", "existingheight", "existingdwellingunits",
            "proposednoofstories", "proposedheight", "proposeddwellingunits"
        ]
        for field in numeric_fields:
            value = getattr(self, field)
            if value == "":
                setattr(self, field, None)
    
        # ✅ Convert date fields
        date_fields = ["currentstatusdate", "filingdate", "firstpermitdate", "permitissuedate"]
        for field in date_fields:
            value = getattr(self, field)
            if isinstance(value, str) and value:
                try:
                    setattr(self, field, transform_date(value))
                except ValueError:
                    logger.warning(f"Invalid date format for {field}: {value}")
                    setattr(self, field, None)
    
        # ✅ Save the object
        super().save(*args, **kwargs)

    
    @classmethod
    def create_async_update_worker(self, endpoint=None, file_name=None):
        async_download_and_update.delay(
            self.get_dataset().id, endpoint=endpoint, file_name=file_name)

    # BIN
    @classmethod
    def download(self, endpoint=None, file_name=None):
        return self.download_file(self.download_endpoint, file_name=file_name)

    @classmethod
    def update_set_filter(self, csv_reader, headers):
        return csv_reader

    # New remapping function to handle new header titles in 2025 data set.
    @classmethod
    def clean_null_bytes_headers(cls, gen_rows):
        try:
            # Extract the header row
            header_row = next(gen_rows)  # Extract the first row (headers)
            logger.info("Processing header row: %s", header_row)
        except StopIteration:
            logger.error("Empty CSV generator received")
            raise ValueError("The CSV file is empty or invalid")
    
        # Header replacements
        replacements = {
            'ownerscity': 'city',
            'ownersstate': 'state',
            'ownerszip': 'zip',
            'firstpermitdate': 'permitissuedate',
        }
    
        # Process header row based on its format
        if isinstance(header_row, dict):  # If the row is a dictionary
            # Update dictionary keys
            for old, new in replacements.items():
                if old in header_row:
                    header_row[new] = header_row.pop(old)
        elif isinstance(header_row, str):  # If the row is a string
            # Replace header strings
            for old, new in replacements.items():
                header_row = header_row.replace(old, new)
        else:
            logger.warning("Unexpected header row type: %s", type(header_row))
        yield header_row
    
        # Process remaining rows
        for row in gen_rows:
            if isinstance(row, dict):  # If the row is a dictionary
                # Clean dictionary values
                for key, value in row.items():
                    if isinstance(value, str):
                        row[key] = value.replace("\0", "").replace("\t", ",")
                yield row
            elif isinstance(row, str):  # If the row is a string
                # Clean string rows
                row = row.replace("\0", "").replace("\t", ",")
                yield row
            else:
                logger.warning("Unexpected row type: %s", type(row))
                yield row

    @classmethod
    def transform_self(cls, file_path, update=None):
        def filter_postcode(row):
            row.pop('Postcode', None)
            row.pop('postcode', None)
            return row
    
        rows = from_csv_file_to_gen(file_path, update)
        cleaned_rows = cls.clean_null_bytes_headers(rows)
    
        logger.info("Applying postcode filter and further transformations...")
    
        expected_fields = [f.name for f in cls._meta.fields]
    
        transformed_rows = []
        for row in with_bbl((filter_postcode(row) for row in cleaned_rows)):
            transformed_row = {field: row.get(field, None) for field in expected_fields}    
            transformed_row["currentstatusdate"] = transform_date(row.get("currentstatusdate"))
            transformed_row["filingdate"] = transform_date(row.get("filingdate"))
            transformed_row["firstpermitdate"] = transform_date(row.get("firstpermitdate"))
            transformed_row["permitissuedate"] = transform_date(row.get("permitissuedate"))
            transformed_rows.append(transformed_row)
    
        return transformed_rows

    @classmethod
    def seed_or_update_self(cls, file_path, **kwargs):
        logger.info("Seeding/Updating %s", cls.__name__)
        count = 0  # Counter for logging progress
    
        def convert_boolean(value):
            if value is None:  # ✅ Handle None correctly
                return None
            if isinstance(value, str):
                value = value.strip().lower()
                if value == "yes":
                    return True
                elif value == "no":
                    return False
                elif value == "":  # Handle empty values
                    return None
            return value  # Return as-is if already True/False/None
    
        boolean_fields = [
            "sprinklerworktype", "plumbingworktype", "littlee", "unmappedccostreet",
            "requestlegalization", "includespermanentremoval", "incompliancewithnycecc",
            "exemptfromnycecc", "standpipe", "antenna", "curbcut", "sign", "fence",
            "scaffold", "shed", "boilerequipmentworktype", "earthworkworktype",
            "foundationworktype", "generalconstructionworktype",
            "mechanicalsystemsworktype", "placeofassemblyworktype",
            "protectionmechanicalmethodsworktype", "sidewalkshedworktype",
            "structuralworktype", "supportofexcavationworktype",
            "temporaryplaceofassemblyworktype"
        ]
    
        def log_progress(row):
            """Log every 10,000 records inserted."""
            nonlocal count
            count += 1
            if count % 10000 == 0:
                logger.info(f"✅ Imported {count} records...")
            return row
    
        def clean_boolean_fields(row):
            """Ensure all boolean fields are converted before inserting."""
            for field in boolean_fields:
                if field in row:
                    row[field] = convert_boolean(row[field])
            return row
    
        processed_rows = (
            log_progress(clean_boolean_fields({k: v for k, v in row.items() if k != "id"}))
            for row in cls.transform_self(file_path=file_path, **kwargs)
        )
        
        for row in processed_rows:
            logger.info(f"Processed Row (before bulk insert): {row}")
            break  # Just log one sample row to avoid spamming logs

    
        cls.bulk_seed(file_path=file_path, data=processed_rows, overwrite=True)    
        logger.info(f"🎯 Import Complete: {count} records inserted.")


    def __str__(self):
        return str(self.jobfilingnumber)
