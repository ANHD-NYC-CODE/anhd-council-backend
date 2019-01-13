from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null, is_older_than, does_not_contain_values
from datasets import models as d_models
import logging

logger = logging.getLogger('app')

# http: // books.agiliq.com / projects / django - orm - cookbook / en / latest / union.html


class DOBPermitIssued():
    # permits = d_models.DOBPermitIssuedLegacy.objects.all().union(d_models.DOBPermitIssuedNow.objects.all())

    def __str__(self):
        return str(self.violationid)
