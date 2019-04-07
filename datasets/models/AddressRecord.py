from django.db import models
from django.db.models import Q
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.database import copy_insert_from_csv, batch_upsert_from_gen
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
            bbl = building['bbl']
            property = ds.Property.objects.get(bbl=bbl)
        except Exception as e:
            return None

        bin = building['bin']
        building_low = building['lhnd'].strip()
        building_high = building['hhnd'].strip()
        building_street = building['stname'].strip()
        building_zip = building['zipcode'].strip()
        building_boro = building['boro'].strip()
        building_number = ds.Building.construct_house_number(building_low,
                                                             building_high)
        if building_number:
            building_number = building_number.strip().replace(' ', '')

        key = self.create_key(number, building_street, code_to_boro(
            building_boro), building_zip, bbl)

        return {
            'key': key,
            'bbl': bbl,
            'bin': bin,
            'number': number,
            'street': building_street,
            'borough': code_to_boro(building_boro),
            'zipcode': building_zip,
            'address': "",
            "buildingnumber": building_number,
            "buildingstreet": building_street,
            "propertyaddress": property.address,
            "alternateaddress": False
        }

    @classmethod
    def generate_rangelist(self, low, high, prefix=None):
        rangelist = []
        cursor = int(low)
        step = 2

        while(cursor <= int(high)):
            if len(str(low)) > 1 and str(low[0]) == '0':
                num_string = '0' + str(cursor)
            else:
                num_string = str(cursor)

            number = str(prefix) + num_string if prefix else num_string
            # preserve z-padded numbers
            rangelist.append(number)
            cursor = cursor + step

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
    def build_building_gen(self, file_path=None):
        logger.debug("Generating Addresses from building csv...")
        building_gen = ds.Building.transform_self(file_path)

        for building in building_gen:
            if re.search(r"(GAR|GARAGE|FRONT|REAR|BEACH|AIR|AIRRGTS|AIR RGTS|WBLDG|EBLDG)", building['stname']):
                pass
            lhnd_split = building['lhnd'].split('-')
            hhnd_split = building['hhnd'].split('-')
            # numbers formatted: 50
            if len(lhnd_split) <= 1:
                low_number, low_letter = self.split_number_letter(building['lhnd'])
                high_number, high_letter = self.split_number_letter(building['hhnd'])
                # create rangelist
                if building['lhnd'].strip() == building['hhnd'].strip():
                    address_row = self.address_row_from_building(number=building['lhnd'].strip(),
                                                                 building=building)
                    if address_row:
                        yield address_row
                else:
                    # For that one number that has a lhnd = 52 and hhnd = 54 1/2
                    # Removing the 1/2 part from the high number
                    if re.search(r'(1/2|1/3|1/4)', low_number):
                        low_number = low_number.split(' ')[0]
                    if re.search(r'(1/2|1/3|1/4)', high_number):
                        high_number = low_number.split(' ')[0]
                    house_numbers = self.generate_rangelist(int(low_number), int(high_number))
                    for number in house_numbers:
                        address_row = self.address_row_from_building(number=number,
                                                                     building=building)
                        if address_row:
                            yield address_row

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
                        low_numbers[1][0], high_numbers[1][0], prefix=low_numbers[0][0] + '-')

                    for number in house_numbers:
                        number = number.strip().replace(' ', '')
                        address_row = self.address_row_from_building(number=number,
                                                                     building=building)
                        if address_row:
                            yield address_row
                else:
                    combined_number = low_numbers[0][0] + "-" + low_numbers[1][0]
                    combined_number = combined_number.strip().replace(' ', '')
                    address_row = self.address_row_from_building(
                        number=combined_number, building=building)
                    if address_row:
                        yield address_row

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
                buildingstreet = building.stname.strip()
                buildingnumber = building.get_house_number()
                if buildingnumber:
                    buildingnumber = buildingnumber.replace(' ', '').strip()
            else:
                building = None
                bin = None
                buildingstreet = None
                buildingnumber = None

            return {
                'key': key,
                'bbl': property.bbl,
                'bin': bin,
                'number': number_letter.strip() if number_letter else None,
                'street': street.strip() if street else None,
                'borough': borough.strip() if borough else None,
                'zipcode': zipcode.strip() if zipcode else None,
                'address': "",
                "buildingnumber": buildingnumber,
                "buildingstreet": buildingstreet,
                "propertyaddress": property.address.strip() if property.address else None,
                "alternateaddress": True
            }

    @classmethod
    def build_property_gen(self):
        logger.debug("Generating Addresses from property objects...")
        for property in ds.Property.objects.all():
            record = self.address_row_from_property(property)
            if record:
                yield record

    @classmethod
    def seed_or_update_self(self, **kwargs):
        self.build_table(file_path=kwargs['file_path'], overwrite=True)

    @classmethod
    def build_table(self, **kwargs):
        file_path = kwargs['file_path']
        batch_size = settings.BATCH_SIZE
        building_gen = self.build_building_gen(file_path=file_path)
        batch_upsert_from_gen(self, building_gen, batch_size, no_conflict=False, **kwargs)
        property_gen = self.build_property_gen()
        batch_upsert_from_gen(self, property_gen, batch_size, no_conflict=True, **kwargs)

        self.build_search()
        logger.debug("Address Record seeding complete!")

    @classmethod
    def build_search(self):
        logger.debug("Updating address search vector: {}".format(self.__name__))
        address_vector = SearchVector('number', weight='A') + SearchVector(
            'street', weight='B') + SearchVector('borough', rank='C') + SearchVector('zipcode', rank='C')
        self.objects.update(address=address_vector)
