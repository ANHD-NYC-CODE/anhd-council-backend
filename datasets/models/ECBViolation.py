# from django.db import models
# from datasets.utils.BaseDatasetModel import BaseDatasetModel
# from core.utils.transform import from_csv_file_to_gen, with_bbl
# from datasets.utils.validation_filters import is_null, is_older_than
# import logging
#
# logger = logging.getLogger(__name__)
#
#
# class ECBViolation(BaseDatasetModel, models.Model):
#     download_endpoint = "https://data.cityofnewyork.us/api/views/3h2n-5cm9/rows.csv?accessType=DOWNLOAD"
#
#     # IsnDobBisExtract: text
#     # EcbViolationNumber: text
#     # EcbViolationStatus: text
#     # DobViolationNumber: text
#     # bin: text
#     # boro: char(1)
#     # block: char(5)
#     # lot: char(4)
#     # bbl: char(10)
#     # HearingDate: date
#     # HearingTime: text
#     # ServedDate: date
#     # IssueDate: date
#     # severity: text
#     # ViolationType: text
#     # RespondentName: text
#     # RespondentHouseNumber: text
#     # RespondentStreet: text
#     # RespondentCity: text
#     # RespondentZip: char(5)
#     # ViolationDescription: text
#     # PenalityImposed: numeric
#     # AmountPaid: numeric
#     # BalanceDue: numeric
#     # InfractionCode1: text
#     # SectionLawDescription1: text
#     # InfractionCode2: text
#     # SectionLawDescription2: text
#     # InfractionCode3: text
#     # SectionLawDescription3: text
#     # InfractionCode4: text
#     # SectionLawDescription4: text
#     # InfractionCode5: text
#     # SectionLawDescription5: text
#     # InfractionCode6: text
#     # SectionLawDescription6: text
#     # InfractionCode7: text
#     # SectionLawDescription7: text
#     # InfractionCode8: text
#     # SectionLawDescription8: text
#     # InfractionCode9: text
#     # SectionLawDescription9: text
#     # InfractionCode10: text
#     # SectionLawDescription10: text
#     # AggravatedLevel: text
#     # HearingStatus: text
#     # CertificationStatus: text
#
#     @classmethod
#     def download(self):
#         return self.download_file(self.download_endpoint)
#
#     @classmethod
#     def pre_validation_filters(self, gen_rows):
#         for row in gen_rows:
#             if is_null(row['isndobbisviol']):
#                 pass
#             row['bbl'] = str(row['bbl'])
#             yield row
#
#     # trims down new update files to preserve memory
#     # uses original header values
#     @classmethod
#     def update_set_filter(self, csv_reader, headers):
#         for row in csv_reader:
#             if is_older_than(row[headers.index('IssueDate')], 4):
#                 pass
#             yield row
#
#     @classmethod
#     def transform_self(self, file_path):
#         return self.pre_validation_filters(with_bbl(from_csv_file_to_gen(file_path)))
#
#     @classmethod
#     def seed_or_update_self(self, **kwargs):
#         logger.info("Seeding/Updating {}", self.__name__)
#         return self.seed_or_update_from_set_diff(**kwargs)
#
#     def __str__(self):
#         return str(self.violationid)
