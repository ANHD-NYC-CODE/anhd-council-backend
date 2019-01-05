from django.db import models
from datasets.utils.Base import Base as BaseDataset
from core.utils.transform import from_csv_file_to_gen, with_bbl

# ACRIS
# combines Real Properties Master (has mortages)
# Real Properties Legal (has bbl)
# Real Properties Parties (has names)
# into 1 table
# joined on document_id
# and linked to buildings with FK bbl


# class AcrisPropertyRecord(BaseDataset, models.Model):
# table_name: real_property_legals
#   fields:
#     DOCUMENTID: text
#     RECORDTYPE: char(1)
#     BOROUGH: smallint
#     BLOCK: integer
#     LOT: integer
#     EASEMENT: boolean
#     PARTIALLOT: char(1)
#     AIRRIGHTS: boolean
#     SUBTERRANEANRIGHTS: boolean
#     PROPERTYTYPE: char(2)
#     STREETNUMBER: text
#     STREETNAME: text
#     UNIT: text
#     GOODTHROUGHDATE: date
# -
#   table_name: real_property_master
#   fields:
#     DOCUMENTID: text
#     RECORDTYPE: char(1)
#     CRFN: text
#     BOROUGH: char(1)
#     DOCTYPE: text
#     DOCDATE: date
#     DOCAMOUNT: bigint
#     RECORDEDFILED: date
#     MODIFIEDDATE: date
#     REELYEAR: smallint
#     REELNBR: integer
#     REELPAGE: integer
#     PCTTRANSFERRED: numeric
#     GOODTHROUGHDATE: date
# -
#   table_name: real_property_parties
#   fields:
#     DOCUMENTID: text
#     RECORDTYPE: char(1)
#     PARTYTYPE: smallint
#     NAME: text
#     ADDRESS1: text
#     ADDRESS2: text
#     COUNTRY: text
#     CITY: text
#     STATE: text
#     ZIP: text
#     GOODTHROUGHDATE: date


#     @classmethod
#     def transform_self(self, file_path):
#         return with_bbl(from_csv_file_to_gen(file_path))
#
#     def __str__(self):
#         return self.document_id
