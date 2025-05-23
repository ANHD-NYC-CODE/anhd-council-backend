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
    """Convert common date/time formats to YYYY-MM-DD, or return None if invalid."""
    if not isinstance(value, str) or not value.strip():
        return None

    value = (
        value.strip()
        .replace('\u200b', '')  # zero-width space
        .replace('\ufeff', '')  # BOM
        .replace('\xa0', ' ')   # non-breaking space
    )

    known_formats = [
        "%m/%d/%Y %I:%M:%S %p",     # e.g. 04/13/2023 12:00:00 AM
        "%m/%d/%Y %H:%M:%S",        # e.g. 04/13/2023 00:00:00
        "%m/%d/%Y",                 # e.g. 04/13/2023
        "%Y-%m-%dT%H:%M:%S.%fZ",    # ISO with microseconds
        "%Y-%m-%dT%H:%M:%S.%f",  
        "%Y-%m-%dT%H:%M:%S",        # ISO no timezone
        "%Y-%m-%d",                 # Simple date
        "%Y/%m/%d",                 # Slash date
        "%Y%m%d",                   # Compact
        "%B %d, %Y %I:%M:%S %p",    # Verbose: March 4, 2025 4:15:24 PM
    ]

    for fmt in known_formats:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue

    logger.warning(f"Format not found - Unable to parse date string: {value}")
    return None


class DOBNowFiledPermit(BaseDatasetModel, models.Model):
    # download_endpoint = "https://data.cityofnewyork.us/api/views/w9ak-ipjd/rows.csv?accessType=DOWNLOAD"
    # download_endpoint = "  https://anhd2402.bpbuild.com/test.csv?accessType=DOWNLOAD"
    base_download_endpoint = "https://data.cityofnewyork.us/resource/w9ak-ipjd.csv"
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
        if self.firstpermitdate:
            self.permitissuedate = self.firstpermitdate
    
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
                    
        if not self.id:  # Allow PostgreSQL to auto-generate the ID
            self.id = None  # Ensure Django does NOT set an explicit ID
            
        # ✅ Save the object
        super().save(*args, **kwargs)

    @classmethod
    def create_async_update_worker(self, endpoint=None, file_name=None):
        async_download_and_update.delay(
            self.get_dataset().id, endpoint=endpoint, file_name=file_name)
    
    @classmethod
    def download(cls, endpoint=None, file_name=None):
        # if endpoint:  # fallback/override behavior still allowed
        #     return cls.download_file(endpoint, file_name=file_name)
        
        fields = [
            "job_filing_number", "bbl", "bin", "block", "lot", 
            "house_no", "street_name", "borough",
            "filing_status", "job_type", "work_on_floor", "filing_date",
            "applicant_first_name", "applicant_last_name", "applicant_professional_title",
            "applicant_license", "owner_s_business_name", "initial_cost",
            "city", "state", "zip"
        ]
        query_string = f"$select={','.join(fields)}&$limit=100000000"
        download_url = f"{cls.base_download_endpoint}?{query_string}"
    
        logger.info(f"📥 Downloading DOB Now filtered dataset from: {download_url}")
        return cls.download_file(download_url, file_name=file_name)

    @classmethod
    def update_set_filter(self, csv_reader, headers):
        return csv_reader

    # New remapping function to handle new header titles in 2025 data set.
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
        logger.debug("🚀 Cleaned header row (ID removed if present): %s", cleaned_header)
    
        # ✅ Header replacements: legacy remaps (already in your code)
        legacy_replacements = {
            'ownerscity': 'city',
            'ownersstate': 'state',
            'ownerszip': 'zip',
            'firstpermitdate': 'permitissuedate',
        }
    
        # ✅ New replacements for Socrata resource API snake_case → camelCase
        socrata_replacements = {
            "job_filing_number": "jobfilingnumber",
            "filing_status": "filingstatus",
            "house_no": "houseno",
            "street_name": "streetname",
            "borough": "borough",
            "bbl": "bbl",
            "bin": "bin",
            "job_type": "jobtype",
            "work_on_floor": "workonfloor",
            "filing_date": "filingdate",
            "applicant_first_name": "applicantfirstname",
            "applicant_last_name": "applicantlastname",
            "applicant_professional_title": "applicantprofessionaltitle",
            "applicant_license": "applicantlicense",
            "owner_s_business_name": "ownersbusinessname",
            "initial_cost": "initialcost",
            "city": "ownerscity",
            "state": "ownersstate",
            "zip": "ownerszip",
        }
    
        # ✅ Merge both replacement maps
        all_replacements = {**legacy_replacements, **socrata_replacements}
    
        # Apply replacements to keys
        remapped_header = {}
        for key, value in cleaned_header.items():
            new_key = all_replacements.get(key, key)
            remapped_header[new_key] = value
    
        logger.info("✅ Remapped Header Row: %s", remapped_header)
    
        yield remapped_header
    
        # ✅ Process remaining rows
        for row in gen_rows:
            if isinstance(row, dict):
                if "id" in row:
                    del row["id"]
                    logger.debug("🚀 Removed 'id' from row: %s", row)
    
                for key, value in row.items():
                    if isinstance(value, str):
                        row[key] = value.replace("\0", "").replace("\t", ",")
    
                yield row
    
            elif isinstance(row, str):
                row = row.replace("\0", "").replace("\t", ",")
                yield row
    
            else:
                logger.warning("⚠️ Unexpected row type: %s", type(row))
                yield row


    @classmethod
    def transform_self(cls, file_path, update=None):
        def filter_postcode(row):
            row.pop('Postcode', None)
            row.pop('postcode', None)
            return row
    
        rows = from_csv_file_to_gen(file_path, update)
        cleaned_rows = cls.clean_null_bytes_headers(rows)
    
        # 🔥 Log the first few rows before transformation
        for i, raw_row in enumerate(cleaned_rows):
            logger.info(f"📝 Raw CSV Row {i}: {raw_row}")
            if i >= 2:  # Only log the first 3 rows
                break
    
        logger.info("Applying postcode filter and further transformations...")
        expected_fields = [f.name for f in cls._meta.fields]
        
        # ✅ Remove "id" from expected fields
        if "id" in expected_fields:
            expected_fields.remove("id")
        
        transformed_rows = []
        for row in with_bbl((filter_postcode(row) for row in cleaned_rows)):
            transformed_row = {field: row.get(field, None) for field in expected_fields if field != "id"}
            transformed_row["currentstatusdate"] = transform_date(row.get("currentstatusdate"))
            transformed_row["filingdate"] = transform_date(row.get("filingdate"))
            transformed_row["firstpermitdate"] = transform_date(row.get("firstpermitdate"))
            transformed_row["permitissuedate"] = transform_date(row.get("firstpermitdate"))
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
            """Log every 50,000 records inserted."""
            nonlocal count
            count += 1
            if count % 50000 == 0:
                logger.info(f"✅ Imported {count} records...")
            return row
    
        def clean_boolean_fields(row):
            """Ensure all boolean fields are converted before inserting."""
            for field in boolean_fields:
                if field in row:
                    row[field] = convert_boolean(row[field])
            return row
    
        transformed_rows = list(cls.transform_self(file_path=file_path, **kwargs))  # Convert generator to list

        if not transformed_rows:
            logger.warning("⚠️ No transformed rows received from CSV. Skipping import.")
            return  # Stop execution if no data exists
        
        processed_rows = [
            log_progress(clean_boolean_fields({k: v for k, v in row.items() if k != "id"}))
            for row in transformed_rows
        ]
        
        if not processed_rows:
            logger.warning("⚠️ No processed rows found after transformation!")
            return
        
        logger.info(f"📊 Ready to insert/update {len(processed_rows)} records.")

        logger.debug("🚀 First Row Before Bulk Insert: %s", processed_rows[0] if processed_rows else "No data")

        if processed_rows:
            for i, row in enumerate(processed_rows[:5]):  # Log first 5 rows
                logger.debug(f"🚀 Sample Row {i+1}: {row}")
            else:
                logger.warning("⚠️ No processed rows found after transformation!")
        
         # ✅ Log first 5 rows
        for i, row in enumerate(processed_rows[:5]):
            logger.debug(f"🚀 Sample Row {i+1}: {row}")
    
        # ✅ Ensure bulk insert actually writes data
        existing_count = cls.objects.count()
        logger.info(f"📊 Records in DB before insert: {existing_count}")
    
        cls.bulk_seed(file_path=file_path, data=processed_rows, overwrite=True)
    
        new_count = cls.objects.count()
        inserted_count = new_count - existing_count

        if inserted_count > 0:
            kwargs['update'].rows_created += inserted_count
            kwargs['update'].save()

        logger.info(f"🎯 Import Complete: {inserted_count} new records inserted. Total: {new_count} records in DB.")


    def __str__(self):
        return str(self.jobfilingnumber)
