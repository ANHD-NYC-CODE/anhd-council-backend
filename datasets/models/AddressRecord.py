from django.db import models, connection, transaction, utils
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
import datetime
from django.dispatch import receiver

logger = logging.getLogger('app')

# Update process: Manual
# Update strategy: Upsert
#
# Download latest
# https://data.cityofnewyork.us/City-Government/Property-Address-Directory/bc8t-ecyu
# Extract ZIP and upload bobaadr.csv file through admin (associated w/ Building model), then update Building, PadRecord, and finally this one when all others finished.
# ** RESOURCE INTENSIVE UPDATE ** - don't run during regular updates after 6pm
# ** Best done on a weekend morning. can take many hours.
# ** May need to run build_search method alone in console if runs out of memory after seeding properties and buildings


class AddressRecord(BaseDatasetModel, models.Model):
    # TODO: add "pad_address field comprised of <lhnd>-<hhnd> <stname>" if building, <address> if property"
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
    pad_address = models.TextField(blank=True, null=True)
    created = models.DateField(blank=True, null=True)

    class Meta:
        indexes = [GinIndex(fields=['address'])]
        unique_together = ('bbl', 'number', 'street')

    @classmethod
    def create_key(self, number, street, borough, zipcode, bbl):
        return str(number).upper() + street.replace(' ', '').upper() + \
            str(borough).upper() + str(zipcode).upper() + str(bbl).upper()

    @classmethod
    def address_row_from_building(self, number='', building=None):
        bbl = building.bbl_id
        bin = building.bin_id
        # removes all letters from number
        number = re.sub(r"[a-zA-Z]", "", number).strip()
        building_low = str(building.lhnd).strip()
        building_high = str(building.hhnd).strip()
        building_street = str(building.stname).strip()
        building_zip = str(building.zipcode).strip()
        building_boro = str(building.boro).strip()
        building_number = ds.Building.construct_house_number(building_low,
                                                             building_high)
        if building_number:
            building_number = building_number.strip().replace(' ', '')

        key = self.create_key(number, building_street, code_to_boro(
            building_boro), building_zip, bbl)

        dict = {
            'key': key,
            'bbl': bbl,
            'bin': bin,
            'number': number.replace('-', ''),  # remove dashes
            'street': building_street,
            'borough': code_to_boro(building_boro),
            'zipcode': building_zip,
            'address': "",  # blank because we build the search vector in build_search method afterwards
            'pad_address': "{}-{} {}".format(building.lhnd, building.hhnd, building.stname),
            'created': datetime.datetime.now().date()
        }

        return dict

    @classmethod
    def generate_rangelist(self, low=0, high=0, prefix=None):
        if not bool(low) and low != 0:
            return []
        rangelist = []
        cursor = int(low)
        step = 2

        while(cursor <= int(high)):
            if len(str(low)) > 1 and str(low)[0] == '0':
                num_string = '0' + str(cursor)
            else:
                num_string = str(cursor)

            number = str(prefix) + num_string if prefix else num_string
            # preserve z-padded numbers
            rangelist.append(number)
            cursor = cursor + step

        return rangelist

    @classmethod
    def split_number_letter(self, house=None):
        if not house:
            return []
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
        # TODO: Switch this to use raw PAD csv
        # Do not create address record for buildings without bbls
        for building in ds.PadRecord.objects.filter(bbl__isnull=False).all():
            try:
                building.bbl
            except Exception as e:
                logger.debug('no BBL record: {} for bin {}'.format(
                    building.bbl_id, building.bin_id))
                continue
            # Do not create addresses for special buildings
            if bool(re.search(r"(GAR|GARAGE|FRONT|REAR|BEACH|AIR|AIRRGTS|AIR RGTS|WBLDG|EBLDG)", building.lhnd.upper())):
                continue
            # Do not create addresses for special buildings
            if bool(re.search(r"(GAR|GARAGE|FRONT|REAR|BEACH|AIR|AIRRGTS|AIR RGTS|WBLDG|EBLDG)", building.hhnd.upper())):
                continue
            # Do not continue if missing a lhnd or hhnd
            if not bool(building.lhnd) or not bool(building.hhnd):
                continue
            lhnd_split = building.lhnd.split('-')
            hhnd_split = building.hhnd.split('-')

            # numbers formatted: 50
            if len(lhnd_split) <= 1:
                low_number, low_letter = self.split_number_letter(
                    building.lhnd)
                high_number, high_letter = self.split_number_letter(
                    building.hhnd)
                # if lhnd is equal to hhnd, number = lhnd
                if building.lhnd.strip() == building.hhnd.strip():
                    address_row = self.address_row_from_building(number=building.lhnd.strip(),
                                                                 building=building)
                    if address_row:
                        yield address_row
                # otherwise, create rangelist of numbers
                else:
                    # For that one number that has a lhnd = 52 and hhnd = 54 1/2
                    # Removing the 1/2 part from the high number
                    if re.search(r'(1/2|1/3|1/4)', low_number):
                        low_number = low_number.split(' ')[0]
                    if re.search(r'(1/2|1/3|1/4)', high_number):
                        high_number = low_number.split(' ')[0]
                    house_numbers = self.generate_rangelist(
                        int(low_number), int(high_number))
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
                    combined_number = low_numbers[0][0] + \
                        "-" + low_numbers[1][0]
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
            # split first instance so 62 West 62nd Street returns West 62nd street
            street = property.address.split(number_letter, 1)[1].strip()
            zipcode = property.zipcode_id
            borough = abrv_to_borough(property.borough)

            number_letter = re.sub(
                r"[a-zA-Z]", "", number_letter)  # removes letter
            key = self.create_key(number_letter, street,
                                  borough, zipcode, property.bbl)

            dict = {
                'key': key,
                'bbl': property.bbl,
                'bin': None,
                'number': number_letter.strip().replace('-', '') if number_letter else None,
                'street': street.strip() if street else None,
                'borough': borough.strip() if borough else None,
                'zipcode': zipcode.strip() if zipcode else None,
                'address': "",  # blank because we build the search vector in build_search method afterwards
                'created': datetime.datetime.now().date()
            }

            return dict

    @classmethod
    def build_property_gen(self):
        logger.debug("Generating Addresses from property objects...")
        for property in ds.Property.objects.all():
            record = self.address_row_from_property(property)
            if record:
                yield record

    @classmethod
    def seed_or_update_self(self, **kwargs):
        self.build_table(overwrite=True)

    @classmethod
    def build_table(self, overwrite=True, **kwargs):
        logger.debug('Building address table from scratch.')
        timestamp = datetime.datetime.now().date()
        property_gen = self.build_property_gen()

        logger.debug('bulk inserting property addresses...')
        batch_upsert_from_gen(
            self, property_gen, settings.BATCH_SIZE, ignore_conflict=False, **kwargs)

        building_gen = self.build_building_gen()

        logger.debug('bulk inserting building addresses...')
        batch_upsert_from_gen(
            self, building_gen, settings.BATCH_SIZE, ignore_conflict=True, **kwargs)

        logger.debug('Building search index...')
        self.build_search()
        logger.debug("Address Record seeding complete!")

        logger.debug("Deleting older records...")
        ds.AddressRecord.objects.filter(created=None).delete()
        ds.AddressRecord.objects.filter(created__lt=timestamp).delete()

    @classmethod
    def build_search(self):
        logger.debug(
            "Updating address search vector: {}".format(self.__name__))
        address_vector = SearchVector('number', weight='A') + SearchVector(
            'street', weight='B') + SearchVector('borough', rank='C') + SearchVector('zipcode', rank='C')
        self.objects.update(address=address_vector)

    def __str__(self):
        return str(self.bbl)


@receiver(models.signals.post_save, sender=AddressRecord)
def timestamp(sender, instance, created, **kwargs):
    if created == True:
        timestamp = datetime.datetime.now().date()
        instance.created = timestamp
        instance.save()
