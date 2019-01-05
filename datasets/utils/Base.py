from core import models as c_models
from core.utils.database import batch_insert_from_file, bulk_insert_from_csv, create_set_from_csvs
from core.utils.typecast import Typecast

import os
import csv

# Testing

# 1) query buildings with > 5 HPD violations total

# OR

# https://docs.djangoproject.com/en/dev/topics/db/queries/#complex-lookups-with-q-objects
# https://stackoverflow.com/questions/739776/django-filters-or

# Custom managers (Model.objects)
# https://docs.djangoproject.com/en/dev/topics/db/managers/#custom-managers

# foreign key that can reference different tables

# Creating a new foreign key with default value from the record

# https://stackoverflow.com/questions/29787853/django-migrations-add-field-with-default-as-function-of-model
# - create migration with nullable foreign key
# - migrate then create migration with default + reverse function and alter to make non-nullable. migrate

# TODO

# 1) Cutoff year?


class Base():
    @classmethod
    def get_dataset(self):
        return c_models.Dataset.objects.filter(model_name=self.__name__).first()

    @classmethod
    def transform_self_from_file(self, file_path):
        return Typecast(self).cast_rows(self.transform_self(file_path))

    @classmethod
    def seed_with_overwrite(self, **kwargs):
        return batch_insert_from_file(self, **kwargs)

    @classmethod
    def bulk_seed(self, **kwargs):
        bulk_insert_from_csv(self, **kwargs)

    @classmethod
    def seed_or_update_from_set_diff(self, **kwargs):
        dataset = c_models.Dataset.objects.filter(model_name=self._meta.model.__name__).first()
        latest_update = dataset.latest_update()
        previous_file = latest_update.file.file if latest_update else None

        if (latest_update and previous_file and os.path.isfile(previous_file.path)):
            new_file_path = kwargs['update'].file.file.path
            create_set_from_csvs(previous_file.path, new_file_path, self, kwargs["update"])
        else:
            return self.bulk_seed(**kwargs)
