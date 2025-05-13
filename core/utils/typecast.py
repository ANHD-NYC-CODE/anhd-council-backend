"""
Typecasting for NYCDB

All values are converted into a suitable python class before
being passed to psycopg2 to be inserted into postgres.
# adaptation-of-python-values-to-sql-types
See http://initd.org/psycopg/docs/usage.html
for how psycopg2 converts python types into postgres types
"""
from django.db import models
from django.contrib.postgres.fields import ArrayField
import copy
import re
import datetime
from decimal import Decimal, InvalidOperation
import logging
import pytz

logger = logging.getLogger('app')

YES_VALUES = [1, True, 'T', 't', 'true',
              'True', 'TRUE', '1', 'y', 'Y', "YES", 'Yes']
NO_VALUES = ['0', 0, False, 'False', 'f', 'F',
             'false', 'FALSE', 'N', 'n', 'NO', 'No', 'no']
INTEGER_TYPES = (models.fields.IntegerField,
                 models.fields.SmallIntegerField, models.fields.BigIntegerField)


def downcase_fields_and_values(d):
    """downcase keys and values in dictionary"""
    return dict((k.lower(), v.strip().lower()) for k, v in d.items())


def integer(i):
    if isinstance(i, int):
        return i
    try:
        int_str = i.strip().replace('$', '')

        if int_str == '.' or int_str == '':
            return None
        elif '.' in i:
            return int(int_str.split('.')[0])
        else:
            return int(int_str)

    except Exception:
        return None


def text(x):
    if x is None:
        return None
    s = str(x).strip()
    if s == '':
        return None
    else:
        return s


def char(x, n):
    if x is None:
        return None
    val = str(x)
    if len(val) > n:
        return val.strip()[0:n]
    else:
        return val.strip()


def numeric(x):
    try:
        return Decimal(x)
    except (InvalidOperation, TypeError):
        return None


# def mm_dd_yyyy(date_str, splitter='/'):
#     try:
#         month, day, year = map(int, date_str[0:10].split('/'))
#         return datetime.date(year, month, day)
#     except ValueError:
#         logger.warning(
#             "mm_dd_yyyy - * Unable to parse date string - {}".format(date_str))
#         return None


# def yyyy_mm_dd(date_str, strptime_format='%Y%m%d'):
#     try:
#         return datetime.datetime.strptime(str(date_str), strptime_format).date()
#     except ValueError:
#         logger.warning(
#             "yyyy_mm_dd - * Unable to parse date string - {}".format(date_str))
#         return None

def mm_dd_yyyy(date_str, splitter='/'):
    """
    Converts a date string in MM/DD/YYYY format to a `datetime.date` object.
    Supports different delimiters (e.g., "/", "-", ".").
    """
    if not date_str or not isinstance(date_str, str):
        logger.warning("mm_dd_yyyy - * Invalid input: {}".format(date_str))
        return None

    try:
        # Split by the specified separator and strip any spaces
        parts = date_str.strip().split(splitter)

        # Ensure the split resulted in exactly 3 parts
        if len(parts) != 3:
            raise ValueError

        # Convert to integers and create a date object
        month, day, year = map(int, parts)
        return datetime.date(year, month, day)

    except ValueError:
        logger.warning("mm_dd_yyyy - * Unable to parse date string: {}".format(date_str))
        return None


def yyyy_mm_dd(date_str, strptime_format='%Y%m%d'):
    """
    Converts a date string in YYYYMMDD or YYYY-MM-DD format to a `datetime.date` object.
    Supports different formats, including `YYYYMMDD` and `YYYY-MM-DD`.
    """
    if not date_str or not isinstance(date_str, str):
        logger.warning("yyyy_mm_dd - * Invalid input: {}".format(date_str))
        return None

    try:
        # Allow both "YYYYMMDD" and "YYYY-MM-DD" formats
        if re.match(r"^\d{8}$", date_str):
            return datetime.datetime.strptime(date_str, "%Y%m%d").date()
        elif re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
            return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        else:
            raise ValueError

    except ValueError:
        logger.warning("yyyy_mm_dd - * Unable to parse date string: {}".format(date_str))
        return None



def date(x):
    """
    Converts various date formats into a Python `date` object.
    """

    if not x or isinstance(x, (datetime.date, datetime.datetime)):
        return x  # Return if already a date/datetime object

    parsed_date = None  # Initialize return variable

    try:
        # ✅ Case 1: YYYYMMDD as an INTEGER (e.g., 20250310 → 2025-03-10)
        if isinstance(x, int) and len(str(x)) == 8:
            parsed_date = datetime.datetime.strptime(str(x), "%Y%m%d").date()

        # ✅ Case 2: Unix Timestamp (Seconds or Milliseconds Since Epoch)
        elif isinstance(x, int) and len(str(x)) in [10, 13]:  # 10 digits (seconds), 13 digits (milliseconds)
            parsed_date = datetime.datetime.fromtimestamp(int(str(x)[:10])).date()

        # ✅ Case 3: Convert string and strip any trailing spaces
        elif isinstance(x, str):
            x = x.strip()

            if len(x) <= 1:
                return None  # Ignore empty strings or single-character inputs

            # ✅ Case 4: YYYYMMDD as a STRING (e.g., "20250310")
            elif re.match(r"^\d{8}$", x):
                parsed_date = datetime.datetime.strptime(x, "%Y%m%d").date()

            # ✅ Case 5: YYYYMMDDHHMMSS as a STRING (e.g., "20250310120000")
            elif re.match(r"^\d{14}$", x):
                parsed_date = datetime.datetime.strptime(x, "%Y%m%d%H%M%S").date()

            # ✅ Case 6: MM/DD/YYYY
            elif re.match(r"^\d{1,2}/\d{1,2}/\d{4}$", x):
                parsed_date = datetime.datetime.strptime(x, "%m/%d/%Y").date()

            # ✅ Case 7: YYYY-MM-DD
            elif re.match(r"^\d{4}-\d{2}-\d{2}$", x):
                parsed_date = datetime.datetime.strptime(x, "%Y-%m-%d").date()

            # ✅ Case 8: YYYY/MM/DD (Slash-separated format)
            elif re.match(r"^\d{4}/\d{2}/\d{2}$", x):
                parsed_date = datetime.datetime.strptime(x, "%Y/%m/%d").date()

            # ✅ Case 9: YYYY-MM-DDTHH:MM:SS.sss (ISO format with milliseconds)
            elif re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+$", x):
                parsed_date = datetime.datetime.strptime(x.split("T")[0], "%Y-%m-%d").date()

            # ✅ Case 10: YYYY-MM-DDTHH:MM:SSZ (ISO UTC format)
            elif re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$", x):
                parsed_date = datetime.datetime.strptime(x.split("T")[0], "%Y-%m-%d").date()

            # ✅ Case 11: YYYY-MM-DDTHH:MM:SS±HH:MM (ISO format with timezone offset)
            elif re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$", x):
                parsed_date = datetime.datetime.strptime(x.split("T")[0], "%Y-%m-%d").date()

            # ✅ Case 12: YYYY-MM-DDTHH:MM (Without Seconds)
            elif re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$", x):
                parsed_date = datetime.datetime.strptime(x.split("T")[0], "%Y-%m-%d").date()

            # ✅ Case 13: Verbose Format (March 4, 2025 4:15:24 PM)
            elif re.match(r"^[A-Za-z]+ \d{1,2}, \d{4} \d{2}:\d{2}:\d{2} (AM|PM)$", x):
                parsed_date = datetime.datetime.strptime(x, "%B %d, %Y %I:%M:%S %p").date()

          # ✅ MM/DD/YYYY HH:MM:SS AM/PM
            elif re.match(r"^\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2}:\d{2} (AM|PM)$", x, re.IGNORECASE):
                parsed_date = datetime.datetime.strptime(x, "%m/%d/%Y %I:%M:%S %p").date()
            # ❌ Case 14: No match found, log warning
            else:
                logger.warning(f"Format not found - Unable to parse date string: {x}")
                return None

    except ValueError:
        logger.warning(f"Unable to parse date string: {x}")
        return None  # Return None if parsing fails

    return parsed_date


def time(x):
    """
    Converts various time formats into a Python `time` object.

    Supports:
    - HH:MM:SS (24-hour format)
    - HH:MM (24-hour format, no seconds)
    - HH:MM AM/PM (12-hour format)
    - HH:MM:SS.sss (Milliseconds)
    - HH:MM:SS.ssssss (Microseconds)
    - HH:MM:SSZ (UTC Zulu time)
    - HH:MM:SS±HH:MM (Time with timezone offset)
    - Unix timestamp (seconds or milliseconds since epoch)
    """

    if isinstance(x, datetime.time):
        return x  # Return if already a time object

    try:
        # ✅ Case 1: Unix Timestamp (Seconds or Milliseconds Since Epoch)
        if isinstance(x, int) and len(str(x)) in [10, 13]:  # 10-digit (seconds), 13-digit (milliseconds)
            return datetime.datetime.utcfromtimestamp(int(str(x)[:10])).time()

        # ✅ Case 2: Convert string and strip any trailing spaces
        elif isinstance(x, str):
            x = x.strip()

            # ✅ Case 3: HH:MM:SS (Standard 24-hour format)
            if re.match(r"^\d{2}:\d{2}:\d{2}$", x):
                return datetime.datetime.strptime(x, "%H:%M:%S").time()

            # ✅ Case 4: HH:MM (No seconds)
            elif re.match(r"^\d{2}:\d{2}$", x):
                return datetime.datetime.strptime(x, "%H:%M").time()

            # ✅ Case 5: HH:MM AM/PM (12-hour format)
            elif re.match(r"^\d{1,2}:\d{2} (AM|PM)$", x, re.IGNORECASE):
                return datetime.datetime.strptime(x, "%I:%M %p").time()

            # ✅ Case 6: HH:MM:SS.sss (Time with milliseconds)
            elif re.match(r"^\d{2}:\d{2}:\d{2}\.\d{1,3}$", x):
                return datetime.datetime.strptime(x, "%H:%M:%S.%f").time()

            # ✅ Case 7: HH:MM:SS.ssssss (Time with microseconds)
            elif re.match(r"^\d{2}:\d{2}:\d{2}\.\d{6}$", x):
                return datetime.datetime.strptime(x, "%H:%M:%S.%f").time()

            # ✅ Case 8: HH:MM:SSZ (Zulu/UTC time)
            elif re.match(r"^\d{2}:\d{2}:\d{2}Z$", x):
                return datetime.datetime.strptime(x[:-1], "%H:%M:%S").time()

            # ✅ Case 9: HH:MM:SS±HH:MM (Time with timezone offset) → Strip offset
            elif re.match(r"^\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$", x):
                return datetime.datetime.strptime(x[:8], "%H:%M:%S").time()

            # ❌ Case 10: No match found, log warning
            else:
                logger.warning(f"Format not found - Unable to parse time string: {x}")
                return None

    except ValueError:
        logger.warning(f"Unable to parse time string: {x}")
        return None  # Return None if parsing fails

    return None  # Default return for invalid cases


def boolean(x):
    if x in YES_VALUES:
        return True
    elif x in NO_VALUES:
        return False
    else:
        return None


def text_array(x, sep=","):
    return x.strip().split(sep)


def char_cast(n):
    # convert to string char
    n = copy.copy(n)

    def to_char(x):
        return char(x, n)

    return to_char


class Typecast():
    def __init__(self, model):
        self.fields = model._meta.fields
        self.cast = self.generate_cast()

    def cast_rows(self, rows):
        """
        input: Iterable
        output: Iterable
        """
        for row in rows:
            yield self.cast_row(row)

    def cast_row(self, row):
        """
        Converts values of dictionary by type of dataset
        input: Dict
        output: Dict
        """
        try:
            d = {}
            for column, val in row.items():
                d[column] = self.cast[column.lower()](val)
            return d
        except:
            # print the row for debugging:
            print(row)
            raise

# isinstance(HPDViolation._meta.get_fields()[1], models.fields.IntegerField)
    def generate_cast(self):
        """
        Generates conversation table for dataset schema
        """
        d = {}
        for field in self.fields:
            if isinstance(field, models.fields.CharField):
                n = int(field.max_length)
                d[field.name] = char_cast(n)
            elif isinstance(field, INTEGER_TYPES):
                d[field.name] = lambda x: integer(x)
            elif isinstance(field, models.fields.TextField):
                d[field.name] = lambda x: text(x)
            elif isinstance(field, models.fields.BooleanField):
                d[field.name] = lambda x: boolean(x)
            elif isinstance(field, models.fields.DateField):
                d[field.name] = lambda x: date(x)
            elif isinstance(field, models.fields.DateTimeField):
                d[field.name] = lambda x: date(x)
            elif isinstance(field, models.fields.TimeField):
                d[field.name] = lambda x: time(x)
            elif isinstance(field, models.fields.DecimalField):
                d[field.name] = lambda x: numeric(x)
            elif isinstance(field, ArrayField):
                d[field.name] = lambda x: text_array(x)
            else:
                d[field.name] = lambda x: x
        return d

class HPDComplaintTypecast(Typecast):
    def cast_row(self, row):
        if 'post_code' in row:
            row['zip'] = row.pop('post_code')
        if 'postcode' in row:
            row['zip'] = row.pop('postcode')
        if 'problemcode' in row:
            row['code'] = row.pop('problemcode')
        if 'problem_code' in row:
            row['code'] = row.pop('problem_code')
        if 'complaintstatus' in row:
            row['status'] = row.pop('complaintstatus')
        if 'complaint_status' in row:
            row['status'] = row.pop('complaint_status')
        if 'complaintstatusdate' in row:
            row['statusdate'] = row.pop('complaintstatusdate')
        if 'councildistrict' in row:
            row['council_district'] = row.pop('councildistrict')
        if 'censustract' in row:
            row['census_tract'] = row.pop('censustract')
        if 'complaint_status_date' in row:
            row['statusdate'] = row.pop('complaint_status_date')
        if 'council_district' in row:
            row['council_district'] = row.pop('council_district')
        if 'complaint_id' in row:
            row['complaintid'] = row.pop('complaint_id')
        if 'building_id' in row:
            row['buildingid'] = row.pop('building_id')
        if 'house_number' in row:
            row['housenumber'] = row.pop('house_number')
        if 'street_name' in row:
            row['streetname'] = row.pop('street_name')
        if 'community_board' in row:
            row['communityboard'] = row.pop('community_board')
        if 'unit_type' in row:
            row['unittype'] = row.pop('unit_type')
        if 'space_type' in row:
            row['spacetype'] = row.pop('space_type')
        if 'received_date' in row:
            row['receiveddate'] = row.pop('received_date')
        if 'problem_id' in row:
            row['problemid'] = row.pop('problem_id')
        if 'major_category' in row:
            row['majorcategory'] = row.pop('major_category')
        if 'minor_category' in row:
            row['minorcategory'] = row.pop('minor_category')
        if 'status_description' in row:
            row['statusdescription'] = row.pop('status_description')
        # Now proceed with the normal casting
        return super().cast_row(row)
