from django.utils import timezone
from django.db import models, transaction
from django.dispatch import receiver
from django.apps import apps
from django.conf import settings
from django_celery_results.models import TaskResult
from core.tasks import async_seed_file, async_seed_table
from datasets import models as dataset_models
from core import models as c_models
from django.utils import timezone

import time
import datetime
import os
import itertools
import logging

logger = logging.getLogger('app')

ACTIVE_MODELS_CHOICES = list(map(lambda model: (model, model), settings.ACTIVE_MODELS))


class Dataset(models.Model):
    name = models.CharField(unique=True, max_length=255, blank=False, null=False)
    model_name = models.CharField(unique=True, max_length=255, blank=False, null=False, choices=ACTIVE_MODELS_CHOICES)
    automated = models.BooleanField(blank=True, null=True)
    update_instructions = models.TextField(blank=True, null=True)

    def model(self):
        return getattr(dataset_models, self.model_name)

    def download(self):
        return getattr(dataset_models, self.model_name).download()

    def download_and_update(self):
        file = getattr(dataset_models, self.model_name).download()
        update = Update.objects.create(dataset=self, file=file)
        return update

    def seed_dataset(self, **kwargs):
        getattr(dataset_models, self.model_name).seed_or_update_self(**kwargs)
        self.delete_old_files()

    def latest_update(self):
        try:
            latest = self.update_set.filter(task_result__status="SUCCESS").latest('created_date')
        except Exception as e:
            latest = None
        return latest

    def latest_file(self):
        return self.datafile_set.latest('uploaded_date')

    def delete_old_files(self):
        # Deletes all but the last 2 files saved for this dataset.
        old_files = self.datafile_set.all().order_by('-uploaded_date')[2:]
        for file in old_files:
            file.delete()

    def __str__(self):
        return self.name


def construct_directory_path(instance, filename):
    split_filename = filename.split('.')
    name = split_filename[0]
    extension = split_filename[1]
    return '{0}/{1}'.format(settings.MEDIA_ROOT, "{0}__{1}.{2}".format(name, timezone.now().strftime("%m%d%Y%H%M%S"), extension))


class DataFile(models.Model):
    file = models.FileField(upload_to=construct_directory_path)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    uploaded_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.file.name


@receiver(models.signals.post_delete, sender=DataFile)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `DataFile` object is deleted.
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


class Update(models.Model):
    file = models.ForeignKey(DataFile, related_name='current_file',
                             on_delete=models.SET_NULL, null=True, blank=True, help_text="File is required for standard updates, Dataset Name required for join table updates")
    previous_file = models.ForeignKey(DataFile, related_name='previous_file',
                                      on_delete=models.SET_NULL, null=True, blank=True)
    dataset = models.ForeignKey(Dataset, on_delete=models.SET_NULL, null=True, blank=True,
                                help_text="File is required for standard updates, Dataset Name required for join table updates")
    rows_updated = models.IntegerField(blank=True, null=True, default=0)
    rows_created = models.IntegerField(blank=True, null=True, default=0)
    total_rows = models.IntegerField(blank=True, null=True)
    created_date = models.DateTimeField(default=timezone.now)
    completed_date = models.DateTimeField(blank=True, null=True)
    task_id = models.CharField(max_length=255, blank=True, null=True)
    task_result = models.ForeignKey(TaskResult, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return str(self.id)


@receiver(models.signals.post_save, sender=Update)
def auto_seed_on_create(sender, instance, created, **kwargs):
    """
    Seeds file in DB
    when corresponding `Update` object is created.
    """

    def on_commit():
        print("commit")
        if created:
            if not instance.dataset and not instance.file:
                raise Exception("File not present")
            elif not instance.dataset:
                instance.dataset = instance.file.dataset

            if instance.file:
                worker = async_seed_file.delay(instance.file.file.path, instance.id)
            else:
                worker = async_seed_table.delay(instance.id)

            instance.task_id = worker.id
            instance.save()
    transaction.on_commit(lambda: on_commit())


@receiver(models.signals.post_save, sender=TaskResult)
def add_task_result_to_update(sender, instance, created, **kwargs):
    def on_commit():
        u = Update.objects.filter(task_id=instance.task_id).first()
        if u:
            u.task_result = instance
            u.completed_date = instance.date_done
            u.save()

    transaction.on_commit(lambda: on_commit())
