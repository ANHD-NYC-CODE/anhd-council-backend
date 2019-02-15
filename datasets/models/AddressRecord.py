from django.db import models
from django.db.models import Q
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.database import copy_insert_from_csv
from core.utils.address import normalize_street
from django.contrib.postgres.search import SearchVector, SearchVectorField
from datasets import models as ds
from core.utils.bbl import code_to_boro
from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
import logging
import re
import os
import csv
import uuid

logger = logging.getLogger('app')

# Update process: Manual
# Update strategy: Upsert
#
# Download latest
# https://data.cityofnewyork.us/City-Government/Property-Address-Directory/bc8t-ecyu
# Extract ZIP and upload bobaadr.csv file through admin, then update


class AddressRecord(BaseDatasetModel, models.Model):
    key = models.TextField(primary_key=True, blank=False, null=False)
    bbl = models.ForeignKey('Property', on_delete=models.SET_NULL, null=True,
                            db_column='bbl', db_constraint=False)
    bin = models.ForeignKey('Building', on_delete=models.SET_NULL, null=True,
                            db_column='bin', db_constraint=False)
    number = models.TextField(blank=True, null=True)
    letter = models.TextField(blank=True, null=True)
    street = models.TextField(blank=True, null=True)
    borough = models.TextField(blank=True, null=True)
    zipcode = models.TextField(blank=True, null=True)
    address = SearchVectorField(blank=True, null=True)

    class Meta:
        indexes = [GinIndex(fields=['address'])]

    @classmethod
    def write_row_from_building(self, number='', letter='', building=None, temp_file_path=None):
        try:
            row = [
                number + letter + building.stname.replace(' ', '') + str(building.boro) + str(building.zipcode) + str(
                    building.bin),
                building.bbl.bbl,
                building.bin,
                number,
                letter,
                building.stname,
                code_to_boro(building.boro),
                building.zipcode,
                ''
            ]
            with open(temp_file_path, 'a') as temp_file:
                writer = csv.writer(temp_file, delimiter=',')
                writer.writerow(row)

        except ds.Property.DoesNotExist as e:
            logger.debug("AddressRecord build - property does not exist")
            return
        except ds.Building.DoesNotExist as e:
            logger.debug("AddressRecord build - building does not exist")
            return
        except Exception as e:
            logger.warning("* Unable to create address for building Table: {}", building)
            return

    @classmethod
    def generate_rangelist(self, low, high, prefix=None):
        rangelist = []
        cursor = int(low)
        step = 2
        while(cursor < int(high)):
            number = str(prefix) + str(cursor) if prefix else str(cursor)
            rangelist.append(number)
            cursor = cursor + step

        number = str(prefix) + str(cursor) if prefix else str(cursor)
        rangelist.append(number)
        return rangelist

    @classmethod
    def split_number_letter(self, house):
        split = re.split('(\d*)', house)
        # 1a outputs: ('', '1', 'a')
        return (split[1], split[2])

    @classmethod
    def build_table_csv(self, **kwargs):
        headers = [field.name for field in self._meta.get_fields()]
        temp_file_path = os.path.join(settings.MEDIA_TEMP_ROOT, str(uuid.uuid4().hex) + '.csv')
        logger.debug("Building Table: {}", self.__name__)
        with open(temp_file_path, 'a') as temp_file:
            writer = csv.writer(temp_file, delimiter=',')
            writer.writerow(headers)

        for building in ds.Building.objects.filter(bbl__isnull=False):
            lhnd_split = building.lhnd.split('-')
            hhnd_split = building.hhnd.split('-')
            # numbers formatted: 50
            if len(lhnd_split) <= 1:
                low_number, low_letter = self.split_number_letter(building.lhnd)
                high_number, high_letter = self.split_number_letter(building.hhnd)
                # create rangelist
                if int(low_number) != int(high_number):
                    house_numbers = self.generate_rangelist(int(low_number), int(high_number))
                    for number in house_numbers:
                        self.write_row_from_building(temp_file_path=temp_file_path, number=number, letter='',
                                                     building=building)
                else:
                    self.write_row_from_building(temp_file_path=temp_file_path, number=low_number, letter=low_letter,
                                                 building=building)

            # numbers formatted: 50-10
            else:
                low_numbers = (self.split_number_letter(lhnd_split[0]), self.split_number_letter(lhnd_split[1]))
                # outputs: ((1, a), (2, a))
                high_numbers = (self.split_number_letter(hhnd_split[0]), self.split_number_letter(hhnd_split[1]))
                # create rangelist
                if int(low_numbers[1][0]) != int(high_numbers[1][0]):
                    house_numbers = self.generate_rangelist(
                        int(low_numbers[1][0]), int(high_numbers[1][0]), prefix=low_numbers[0][0] + '-')
                    for number in house_numbers:
                        self.write_row_from_building(temp_file_path=temp_file_path,
                                                     number=number, letter='', building=building)
                else:
                    combined_number = low_numbers[0][0] + "-" + low_numbers[1][0]
                    self.write_row_from_building(temp_file_path=temp_file_path,
                                                 number=combined_number, letter='', building=building)

        return temp_file_path

    @classmethod
    def seed_or_update_self(self, **kwargs):
        self.build_table(overwrite=True)

    @classmethod
    def build_table(self, **kwargs):
        csv_path = self.build_table_csv(**kwargs)
        copy_insert_from_csv(self._meta.db_table, csv_path, **kwargs)
        self.build_search()

    @classmethod
    def build_search(self):
        logger.debug("Updating address search vector: {}".format(self.__name__))
        address_vector = SearchVector('number', weight='A') + SearchVector('letter', weight='D') + SearchVector(
            'street', weight='B') + SearchVector('borough', rank='C') + SearchVector('zipcode', rank='C')
        self.objects.update(address=address_vector)
