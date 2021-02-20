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


def mm_dd_yyyy(date_str, splitter='/'):
    try:
        month, day, year = map(int, date_str[0:10].split('/'))
        return datetime.date(year, month, day)
    except ValueError:
        logger.warning(
            "mm_dd_yyyy - * Unable to parse date string - {}".format(date_str))
        return None


def yyyy_mm_dd(date_str, strptime_format='%Y%m%d'):
    try:
        return datetime.datetime.strptime(str(date_str), strptime_format).date()
    except ValueError:
        logger.warning(
            "yyyy_mm_dd - * Unable to parse date string - {}".format(date_str))
        return None


def date(x):
    if not x or isinstance(x, (datetime.date, datetime.datetime)):
        return x

    parsed_date = None
    # checks yyyymmdd format in integers
    if isinstance(x, int):
        if len(str(x)) == 8:
            parsed_date = yyyy_mm_dd(x, '%Y%m%d')
    elif isinstance(x, str):
        x = x.strip()  # because DOB Permits Issued has a trailing space at the end... :(
        # Filters bad string entries
        if len(x.strip()) == 1:
            parsed_date = None
        # checks string dates
        # checks for 20181231 date input
        elif re.match(r'[0-9]{8}', x):
            try:
                parsed_date = yyyy_mm_dd(x, '%Y%m%d')
            except ValueError:
                logger.warning(
                    "r'[0-9]\{\8\}', * Unable to parse date string - {}".format(x))
                parsed_date = None

        elif (len(x.strip()) == 8 or len(x.strip()) == 9 or len(x.strip()) == 10) and len(x.split('/')) == 3:
            # checks for 1/1/2018 date input
            # checks for 1/01/2018 date input
            # checks for 01/01/2018 date input
            parsed_date = mm_dd_yyyy(x, '/')
        elif (len(x.strip()) == 8 or len(x.strip()) == 9 or len(x.strip()) == 10) and len(x.split('-')) == 3:
            # checks for 2018-11-01 format
            parsed_date = yyyy_mm_dd(x, '%Y-%m-%d')
        elif len(x.strip()) == 22 and len(x[0:10].split('/')) == 3:
            # checks for 12/31/2018 12:00:00 AM date input
            parsed_date = mm_dd_yyyy(x, '/')
        elif len(x.strip()) == 19 and len(x[0:10].split('/')) == 3:
            # checks for 12/31/2018 12:00:00 date input
            parsed_date = mm_dd_yyyy(x, '/')
        elif len(x.split('T')[0]) == 10 and len(x.split('T')[0]).split('-')) == 3:
            # checks for 2017-02-06T00:00:00000
            parsed_date=yyyy_mm_dd(x.split('T')[0], '%Y-%m-%d')
        else:
            logger.warning(
                " Format not found - * Unable to parse date string - {}".format(x))
            parsed_date=None

    return parsed_date


def time(x):
    """
    Converts string into datetime.time
    Example input: 13:01:00
    """
    if isinstance(x, datetime.time):
        return x
    if isinstance(x, str) and re.match(r'^\d{2}:\d{2}:\d{2}$', x.strip()):
        try:
            return datetime.time(*map(int, x.strip().split(':')))
        except ValueError:
            return None


def boolean(x):
    if x in YES_VALUES:
        return True
    elif x in NO_VALUES:
        return False
    else:
        return None


def text_array(x, sep = ","):
    return x.strip().split(sep)


def char_cast(n):
    # convert to string char
    n=copy.copy(n)

    def to_char(x):
        return char(x, n)

    return to_char


class Typecast():
    def __init__(self, model):
        self.fields=model._meta.fields
        self.cast=self.generate_cast()

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
            d={}
            for column, val in row.items():
                d[column]=self.cast[column.lower()](val)
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
        d={}
        for field in self.fields:
            if isinstance(field, models.fields.CharField):
                n=int(field.max_length)
                d[field.name]=char_cast(n)
            elif isinstance(field, INTEGER_TYPES):
                d[field.name]=lambda x: integer(x)
            elif isinstance(field, models.fields.TextField):
                d[field.name] = lambda x: text(x)
            elif isinstance(field, models.fields.BooleanField):
                d[field.name]=lambda x: boolean(x)
            elif isinstance(field, models.fields.DateField):
                d[field.name]=lambda x: date(x)
            elif isinstance(field, models.fields.DateTimeField):
                d[field.name]=lambda x: date(x)
            elif isinstance(field, models.fields.TimeField):
                d[field.name]=lambda x: time(x)
            elif isinstance(field, models.fields.DecimalField):
                d[field.name]=lambda x: numeric(x)
            elif isinstance(field, ArrayField):
                d[field.name]=lambda x: text_array(x)
            else:
                d[field.name]=lambda x: x
        return d
