from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null
from datasets import models as ds
from core.utils.bbl import boro_to_abrv
from core.utils.address import clean_number_and_streets, get_house_number, get_street, get_borough, remove_building_terms
import requests
import json
import re
import logging
from django.dispatch import receiver
from core.tasks import async_download_and_update


logger = logging.getLogger('app')


class Eviction(BaseDatasetModel, models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['bbl', '-executeddate']),
            models.Index(fields=['-executeddate']),

        ]
        unique_together = ('evictionaddress', 'evictionaptnum', 'executeddate', 'marshallastname')

    download_endpoint = "https://data.cityofnewyork.us/api/views/6z8x-wfk4/rows.csv?accessType=DOWNLOAD"
    API_ID = '6z8x-wfk4'
    QUERY_DATE_KEY = 'executeddate'

    courtindexnumber = models.TextField(primary_key=True, blank=False, null=False)
    bbl = models.ForeignKey('Property', db_column='bbl', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=True)
    borough = models.TextField(blank=True, null=True)
    docketnumber = models.TextField(blank=True, null=True)
    evictionaddress = models.TextField(blank=True, null=True)
    evictionaptnum = models.TextField(blank=True, null=True)
    evictionzip = models.TextField(blank=True, null=True)
    uniqueid = models.TextField(blank=True, null=True)
    executeddate = models.DateTimeField(db_index=True, blank=True, null=True)
    marshalfirstname = models.TextField(blank=True, null=True)
    marshallastname = models.TextField(blank=True, null=True)
    residentialcommercialind = models.TextField(db_index=True, blank=True, null=True)
    schedulestatus = models.TextField(db_index=True, blank=True, null=True)
    cleaned_address = models.TextField(blank=True, null=True)
    geosearch_address = models.TextField(blank=True, null=True)

    slim_query_fields = ["courtindexnumber", "bbl", "executeddate"]

    @classmethod
    def create_async_update_worker(self):
        async_download_and_update.delay(self.get_dataset().id)

    @classmethod
    def download(self):
        return self.download_file(self.download_endpoint)

    @classmethod
    def pre_validation_filters(self, gen_rows):
        for row in gen_rows:
            if is_null(row['courtindexnumber']):
                continue
            yield row

    @classmethod
    def update_set_filter(self, csv_reader, headers):
        return csv_reader

    @classmethod
    def clean_evictions_csv(self, gen_rows):
        for row in gen_rows:
            row = row.upper()
            row = row.upper().replace(',JR.', ' JR')
            row = row.upper().replace(', JR.', ' JR')

            row = clean_number_and_streets(row, True)
            yield row.upper().strip()

    @classmethod
    def save_eviction(self, eviction=None, bbl=None, cleaned_address=None, geosearch_address=None):
        if bbl:
            eviction.bbl = bbl
        if cleaned_address:
            eviction.cleaned_address = cleaned_address
        if geosearch_address:
            eviction.geosearch_address = geosearch_address
        eviction.save()

    @classmethod
    def view_address_results(self, evictions):
        for eviction in evictions:
            print("Original: ", eviction.evictionaddress)
            print("Cleaned: ", eviction.cleaned_address)
            print("Geosearch: ", eviction.geosearch_address)
            print("************************************")

    @classmethod
    def link_eviction_to_pluto_by_address(self):

        evictions = self.objects.filter(bbl__isnull=True)
        for eviction in evictions:
            # matches STREET or STREET EAST / WEST etc
            pattern = r'[0-9].*?(\bLANE|\bHIGHWAY|\bSQUARE|\bEXPRESSWAY|\bPARKWAY|\bPARK|\bSTREET|\bAVENUE|\bPLACE|\bBOULEVARD|\bDRIVE|\bROAD|\bCONCOURSE|\bPLAZA|\bTERRACE|\bCOURT|\bLOOP|\bCIRCLE)(\sNORTH|\sSOUTH|\sEAST|\sWEST)?'

            # pattern = r'[0-9].*?((\bLANE (\bWEST|\bEAST|\bNORTH|\bSOUTH)|\bLANE)|(\bHIGHWAY (\bWEST|\bEAST|\bNORTH|\bSOUTH)|\bHIGHWAY)|(\bSQUARE (\bWEST|\bEAST|\bNORTH|\bSOUTH)|\bSQUARE)|(\bEXPRESSWAY (\bWEST|\bEAST|\bNORTH|\bSOUTH)|\bEXPRESSWAY)|(\bPARKWAY (\bWEST|\bEAST|\bNORTH|\bSOUTH)|\bPARKWAY)|(\bPARK (\bWEST|\bEAST|\bNORTH|\bSOUTH)|\bPARK)|(\bSTREET (\bWEST|\bEAST|\bNORTH|\bSOUTH)|\bSTREET)|((\bAVENUE \w\b (\bWEST|\bEAST|\bNORTH|\bSOUTH)|\bAVENUE \w\b)|(\bAVENUE (\bWEST|\bEAST|\bNORTH|\bSOUTH)|\bAVENUE))|(\bPLACE (\bWEST|\bEAST|\bNORTH|\bSOUTH)|\bPLACE)|(\bBOULEVARD (\bWEST|\bEAST|\bNORTH|\bSOUTH)|\bBOULEVARD)|(\bDRIVE (\bWEST|\bEAST|\bNORTH|\bSOUTH)|\bDRIVE)|(\bROAD (\bWEST|\bEAST|\bNORTH|\bSOUTH)|\bROAD)|(\bCONCOURSE (\bWEST|\bEAST|\bNORTH|\bSOUTH)|\bCONCOURSE)|(\bPLAZA (\bWEST|\bEAST|\bNORTH|\bSOUTH)|\bPLAZA)|(\bTERRACE (\bWEST|\bEAST|\bNORTH|\bSOUTH)|\bTERRACE)|(\bCOURT (\bWEST|\bEAST|\bNORTH|\bSOUTH)|\bCOURT)|(\bLOOP (\bWEST|\bEAST|\bNORTH|\bSOUTH)|\bLOOP)|(\bCRESCENT (\bWEST|\bEAST|\bNORTH|\bSOUTH)|\bCRESCENT)|(\bBROADWAY (\bWEST|\bEAST|\bNORTH|\bSOUTH)|\bBROADWAY)|(\bWAY (\bWEST|\bEAST|\bNORTH|\bSOUTH)|\bWAY)|(\bWALK (\bWEST|\bEAST|\bNORTH|\bSOUTH)|\bWALK)|(\bTURNPIKE (\bWEST|\bEAST|\bNORTH|\bSOUTH)|\bTURNPIKE)|(\bPROMENADE (\bWEST|\bEAST|\bNORTH|\bSOUTH)|\bPROMENADE)|(\bRIDGE (\bWEST|\bEAST|\bNORTH|\bSOUTH)|\bRIDGE)|(\bOVAL (\bWEST|\bEAST|\bNORTH|\bSOUTH)|\bOVAL)|(\bSLIP (\bWEST|\bEAST|\bNORTH|\bSOUTH)|\bSLIP)|(\bCIRCLE (\bWEST|\bEAST|\bNORTH|\bSOUTH)|\bCIRCLE))'

            # pattern = r'[0-9].*?(\bLANE|\bEXPRESSWAY|\bPARKWAY|\bSTREET|(\bAVENUE \w\b|\bAVENUE)|\bPLACE|\bBOULEVARD|\bDRIVE|\bROAD|\bCONCOURSE|\bPLAZA|\bTERRACE|\bCOURT|\bLOOP|\bCRESENT|\bBROADWAY|\bWAY|\bWALK|\bTURNPIKE|\bPROMENADE|\bRIDGE|\bOVAL|\bSLIP|\bCIRCLE)'
            match = re.search(pattern, eviction.evictionaddress.upper())
            if match:
                cleaned_address = match.group(0)
                # TODO: remove house letter from cleaned address
                self.save_eviction(eviction=eviction, cleaned_address=cleaned_address)
                address_match = ds.AddressRecord.objects.filter(
                    address=cleaned_address + ' {}'.format(eviction.borough))
                if len(address_match) == 1:
                    try:
                        self.save_eviction(eviction=eviction, bbl=address_match[0].bbl)
                    except Exception as e:
                        logger.warning(e, address_match.key, address_match[0].bbl_id)
                        raise e

                elif len(address_match) > 1:
                    # not a super generic query like 123 STREET or 45 AVENUE
                    if not re.match(r"(\d+ (\bSTREET|\bAVENUE))", cleaned_address):
                        try:
                            self.save_eviction(eviction=eviction, bbl=address_match[0].bbl)
                        except Exception as e:
                            logger.warning(e, address_match.key, address_match[0].bbl_id)
                            raise e
                    else:
                        # logger.debug(
                        #     "no eviction match - multiple matches found on generic address: {}".format(eviction.evictionaddress))
                        self.get_geosearch_address("{}, {}".format(cleaned_address, eviction.borough), eviction)
                else:
                    # logger.debug("no eviction match - no address matches: {}".format(eviction.evictionaddress))
                    self.get_geosearch_address("{}, {}".format(cleaned_address, eviction.borough), eviction)

            else:
                logger.debug("no eviction match - no regex matches: {}".format(eviction.evictionaddress))

    @classmethod
    def get_geosearch_address(self, cleaned_address, eviction):
        response = requests.get(
            "https://geosearch.planninglabs.nyc/v1/search?text={}".format("{}, {}".format(cleaned_address, eviction.borough)))
        try:
            parsed = json.loads(response.text)
        except Exception as e:
            logger.debug('Unable to parse response from query: {}'.format(address_search_query))
            return None

        match = None
        # First compare the borough and zipcode of geosearch and cleaned address
        for feature in parsed['features']:
            if 'borough' not in feature['properties'] or 'postalcode' not in feature['properties']:
                logger.debug('Geosearch result not usable without borough or postalcode: {}'.format(
                    feature['properties']))
                return None
            if feature['properties']['borough'].upper() == eviction.borough and feature['properties']['postalcode'] == eviction.evictionzip:
                match = feature['properties']

        # next compare the house and street numbers
        if match and self.validate_geosearch_match(match, cleaned_address):
            try:
                bbl = ds.Property.objects.get(bbl=match['pad_bbl'])

                self.save_eviction(eviction=eviction, bbl=bbl, geosearch_address=match['label'])
            except Exception as e:
                self.save_eviction(eviction=eviction, geosearch_address=match['label'])
                logger.warning('unable to match response bbl {} to a db record'.format(match['pad_bbl']))
                return None
        else:
            if match:
                logger.debug('Match invalid - geosearch: {} vs. cleaned: {}'.format(match['label'], cleaned_address))
                self.save_eviction(eviction=eviction, geosearch_address=match['label'])
            else:
                logger.debug('No Match found for cleaned_address: {}', cleaned_address)

            return None

    @classmethod
    def validate_geosearch_match(self, geosearch_match, cleaned_address):
        if not geosearch_match:
            return False

        # remove apostrophes
        geosearch_match['label'] = re.sub(r"\'", '', geosearch_match['label'])
        # without borough, New York, NY, USA tokens
        geosearch_house_street = remove_building_terms(geosearch_match['label'].split(', ')[0].upper())
        geosearch_borough = geosearch_match['label'].split(', ')[1].upper()

        geosearch = ', '.join([clean_number_and_streets(geosearch_house_street, True), geosearch_borough]).upper()
        if geosearch == cleaned_address:
            # First naive match against house + street + borough
            return True
        elif get_street(geosearch_house_street) == get_street(cleaned_address) and geosearch_borough == get_borough(cleaned_address):
            # if street and borough match, check for number range matches
            geo_house = get_house_number(geosearch_house_street)
            cleaned_house = get_house_number(cleaned_address)
            if geo_house == cleaned_house:
                # try explicit match against house without apartment number + street + borough
                return True
            elif '-' in cleaned_house and geo_house in cleaned_house:
                # try explict match against segment in a "-" number
                return True
            elif "-" in cleaned_house:
                # Step from low to high and see if geosearch number matches anything
                low, high = cleaned_house.split('-', 1)
                cursor = int(low)
                step = 2
                while(cursor <= int(high)):
                    if int(geo_street) == cursor:
                        return True
                    cursor = cursor + step
            else:
                return False
        else:
            return False

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(from_csv_file_to_gen(file_path, update, self.clean_evictions_csv))

    @classmethod
    def seed_or_update_self(self, **kwargs):
        logger.debug("Seeding/Updating {}", self.__name__)
        update = self.seed_with_upsert(**kwargs)
        self.link_eviction_to_pluto_by_address()
        logger.debug('annotating properties for {}', self.__name__)
        self.annotate_properties()
        return update

    @classmethod
    def annotate_properties(self):
        self.annotate_all_properties_standard()

    def __str__(self):
        return str(self.courtindexnumber)


@receiver(models.signals.post_save, sender=Eviction)
def annotate_property_on_save(sender, instance, created, **kwargs):
    if created == True:
        try:

            annotation = sender.annotate_property_standard(ds.PropertyAnnotation.objects.get(bbl=instance.bbl))
            annotation.save()
        except Exception as e:
            logger.warning(e)
