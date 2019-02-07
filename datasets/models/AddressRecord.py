from django.db import models
from django.db.models import Q
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.database import batch_upsert_from_gen
from core.utils.address import normalize_street
from django.contrib.postgres.search import SearchVector, SearchVectorField
from datasets import models as ds
from core.utils.bbl import code_to_boro
from django.conf import settings
from django.contrib.postgres.indexes import GinIndex

import logging
import re

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
    def create_address_from_building(self, number='', letter='', building=None):
        try:
            record = {}
            record['key'] = "{}{}{}{}{}{}".format(number, letter, "".join(
                building.stname.split()), building.boro, building.zipcode, building.bin)
            record['bbl'] = building.bbl.bbl
            record['bin'] = building.bin
            record['zipcode'] = building.zipcode
            record['borough'] = code_to_boro(building.boro)
            record['street'] = building.stname
            record['letter'] = letter
            record['number'] = number
            return record
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
    def build_table_gen(self, **kwargs):

        logger.debug("Building Table: {}", self.__name__)

        for building in ds.Building.objects.all():
            lhnd_split = building.lhnd.split('-')
            hhnd_split = building.hhnd.split('-')
            if len(lhnd_split) <= 1:
                # numbers formatted: 50
                low_number, low_letter = self.split_number_letter(building.lhnd)
                high_number, high_letter = self.split_number_letter(building.hhnd)
                # create rangelist
                if int(low_number) != int(high_number):
                    house_numbers = self.generate_rangelist(int(low_number), int(high_number))
                    for number in house_numbers:
                        address = self.create_address_from_building(number=number, letter='', building=building)
                        if address:
                            yield address
                else:
                    address = self.create_address_from_building(number=low_number, letter=low_letter, building=building)
                    if address:
                        yield address

            else:
                # numbers formatted: 50-10
                low_numbers = (self.split_number_letter(lhnd_split[0]), self.split_number_letter(lhnd_split[1]))
                # outputs: ((1, a), (2, a))
                high_numbers = (self.split_number_letter(hhnd_split[0]), self.split_number_letter(hhnd_split[1]))
                # create rangelist
                if int(low_numbers[1][0]) != int(high_numbers[1][0]):
                    house_numbers = self.generate_rangelist(
                        int(low_numbers[1][0]), int(high_numbers[1][0]), prefix=low_numbers[0][0] + '-')
                    for number in house_numbers:
                        address = self.create_address_from_building(number=number, letter='', building=building)
                        if address:
                            yield address
                else:
                    combined_number = low_numbers[0][0] + "-" + low_numbers[1][0]
                    address = self.create_address_from_building(
                        number=combined_number, letter=None, building=building)
                    if address:
                        yield address

    @classmethod
    def build_table(self, **kwargs):
        rows = self.build_table_gen(**kwargs)
        batch_upsert_from_gen(self, rows, settings.BATCH_SIZE)
        self.build_search()

    @classmethod
    def build_search(self):
        logger.debug("Updating address search vector: {}".format(self.__name__))
        address_vector = SearchVector('number', weight='A') + SearchVector('letter', weight='D') + SearchVector(
            'street', weight='B') + SearchVector('borough', rank='C') + SearchVector('zipcode', rank='C')
        self.objects.update(address=address_vector)
