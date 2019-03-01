from django.db import models
from django.db.models import Q
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.database import copy_insert_from_csv, batch_upsert_from_gen
from core.utils.address import normalize_street
from django.contrib.postgres.search import SearchVector, SearchVectorField
from datasets import models as ds
from core.utils.bbl import code_to_boro, abrv_to_borough
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
    street = models.TextField(blank=True, null=True)
    borough = models.TextField(blank=True, null=True)
    zipcode = models.TextField(blank=True, null=True)
    address = SearchVectorField(blank=True, null=True)
    buildingnumber = models.TextField(blank=True, null=True)
    buildingstreet = models.TextField(blank=True, null=True)
    propertyaddress = models.TextField(blank=True, null=True)
    alternateaddress = models.BooleanField(blank=True, null=True)

    class Meta:
        indexes = [GinIndex(fields=['address'])]

    @classmethod
    def create_key(self, number, street, borough, zipcode, bbl):
        return str(number).upper() + street.replace(' ', '').upper() + \
            str(borough).upper() + str(zipcode).upper() + str(bbl).upper()

    @classmethod
    def address_row_from_building(self, number='', building=None):
        try:
            property = building.bbl
            bbl = property.bbl
        except Exception as e:
            return

        try:
            bin = building.bin
        except Exception as e:
            bin = None

        key = self.create_key(number, building.stname, code_to_boro(
            building.boro), building.zipcode, building.bbl)

        return {
            'key': key,
            'bbl': bbl,
            'bin': bin,
            'number': number,
            'street': building.stname,
            'borough': code_to_boro(building.boro),
            'zipcode': building.zipcode,
            'address': "",
            "buildingnumber": building.get_house_number(),
            "buildingstreet": building.stname,
            "propertyaddress": property.address,
            "alternateaddress": False
        }

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
        # This gets number and 1/2 lol
        # (^([^\s]* (1\/2|1\/3|1\/4))|^[^\s]*)

        letter = re.search(r"[a-zA-Z]+", house)
        if letter:
            letter = letter.group()
            number = house.split(letter)[0]
        else:
            letter = ''
            number = house

        return (number, letter)

    @classmethod
    def build_building_gen(self):
        for building in ds.Building.objects.filter(bbl__isnull=False):
            lhnd_split = building.lhnd.split('-')
            hhnd_split = building.hhnd.split('-')
            # numbers formatted: 50
            if len(lhnd_split) <= 1:
                low_number, low_letter = self.split_number_letter(building.lhnd)
                high_number, high_letter = self.split_number_letter(building.hhnd)
                # create rangelist
                if building.lhnd.strip() == building.hhnd.strip():
                    yield self.address_row_from_building(number=building.lhnd.strip(),
                                                         building=building)
                else:
                    # For that one number that has a lhnd = 52 and hhnd = 54 1/2
                    # Removing the 1/2 part from the high number
                    if re.search(r'(1/2|1/3|1/4)', low_number):
                        low_number = low_number.split(' ')[0]
                    if re.search(r'(1/2|1/3|1/4)', high_number):
                        high_number = low_number.split(' ')[0]
                    house_numbers = self.generate_rangelist(int(low_number), int(high_number))
                    for number in house_numbers:
                        yield self.address_row_from_building(number=number,
                                                             building=building)

            # numbers formatted: 50-10
            else:
                low_numbers = (self.split_number_letter(
                    lhnd_split[0]), self.split_number_letter(lhnd_split[1]))
                # outputs: ((1, a), (2, a))
                high_numbers = (self.split_number_letter(
                    hhnd_split[0]), self.split_number_letter(hhnd_split[1]))
                # create rangelist
                if low_numbers[1][0].strip() != high_numbers[1][0].strip():
                    house_numbers = self.generate_rangelist(
                        int(low_numbers[1][0]), int(high_numbers[1][0]), prefix=low_numbers[0][0] + '-')
                    for number in house_numbers:
                        yield self.address_row_from_building(number=number,
                                                             building=building)
                else:
                    combined_number = low_numbers[0][0] + "-" + low_numbers[1][0]
                    yield self.address_row_from_building(
                        number=combined_number, building=building)

    @classmethod
    def address_row_from_property(self, property):
        if not property.address:
            return

        number_letter = re.search(r"(?=\d*)^.*?(?=\s\b)", property.address)

        if number_letter:
            number_letter = number_letter.group()
            street = property.address.split(number_letter)[1].strip()
            zipcode = property.zipcode
            borough = abrv_to_borough(property.borough)

            key = self.create_key(number_letter, street, borough, zipcode, property.bbl)

            property_buildings = property.building_set.all()
            if property_buildings.count() == 1:
                # Try to return some building info if property only has 1 building
                building = property_buildings.first()
                bin = building.bin
                buildingstreet = building.stname
                buildingnumber = building.get_house_number()
            else:
                building = None
                bin = None
                buildingstreet = None
                buildingnumber = None

            return {
                'key': key,
                'bbl': property.bbl,
                'bin': bin,
                'number': number_letter,
                'street': street,
                'borough': borough,
                'zipcode': zipcode,
                'address': "",
                "buildingnumber": buildingnumber,
                "buildingstreet": buildingstreet,
                "propertyaddress": property.address,
                "alternateaddress": True
            }

    @classmethod
    def build_property_gen(self):
        for property in ds.Property.objects.all():
            record = self.address_row_from_property(property)
            if record:
                yield record

    @classmethod
    def seed_or_update_self(self, **kwargs):
        self.build_table(overwrite=True)

    @classmethod
    def build_table(self, **kwargs):
        batch_size = 1000000
        # csv_path = self.build_table_csv()
        # copy_insert_from_csv(self._meta.db_table, csv_path, **kwargs)
        building_gen = self.build_building_gen()
        batch_upsert_from_gen(self, building_gen, batch_size, no_conflict=False, **kwargs)
        property_gen = self.build_property_gen()
        batch_upsert_from_gen(self, property_gen, batch_size, no_conflict=True, **kwargs)

        self.build_search()

    @classmethod
    def build_search(self):
        logger.debug("Updating address search vector: {}".format(self.__name__))
        address_vector = SearchVector('number', weight='A') + SearchVector(
            'street', weight='B') + SearchVector('borough', rank='C') + SearchVector('zipcode', rank='C')
        self.objects.update(address=address_vector)
