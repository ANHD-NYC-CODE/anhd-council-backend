from django.utils import timezone
from django.db import models, transaction
from django.dispatch import receiver
from django.apps import apps

from .utils.utility import dict_to_model
from .utils.database import insert_rows
from django_celery_results.models import TaskResult
from datasets.models import Building
import time
import os
import itertools

ACTIVE_MODELS = ['HPDViolation', 'Building', 'Council']
ACTIVE_MODELS_CHOICES = list(map(lambda model: (model, model), ACTIVE_MODELS))


class Dataset(models.Model):
    name = models.CharField(unique=True, max_length=255, blank=False, null=False)
    model_name = models.CharField(unique=True, max_length=255, blank=False, null=False, choices=ACTIVE_MODELS_CHOICES)
    download_endpoint = models.TextField(blank=True, null=True)
    uploaded_date = models.DateTimeField(default=timezone.now)

    def transform_dataset(self, file_path):
        return eval(self.model_name).transform_self(file_path)

    def latest_file(self):
        return self.datafile_set.latest('uploaded_date')

    def __str__(self):
        return self.name


def construct_directory_path(instance, filename):
    return '{0}/{1}'.format('./', "{0}-{1}".format(time.time(), filename))


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
    file = models.ForeignKey(DataFile, on_delete=models.SET_NULL, null=True)
    dataset = models.ForeignKey(Dataset, on_delete=models.SET_NULL, null=True)
    model_name = models.CharField(max_length=255, blank=False, null=False,
                                  choices=ACTIVE_MODELS_CHOICES)
    rows_updated = models.IntegerField(blank=True, null=True, default=0)
    rows_created = models.IntegerField(blank=True, null=True, default=0)
    created_date = models.DateTimeField(default=timezone.now)
    completed_date = models.DateTimeField(blank=True, null=True)
    task_id = models.CharField(max_length=255, blank=True, null=True)
    task_result = models.ForeignKey(TaskResult, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.dataset.name


@receiver(models.signals.post_save, sender=Update)
def auto_seed_file_on_create(sender, instance, created, **kwargs):
    """
    Seeds file in DB
    when corresponding `Update` object is created.
    """

    def on_commit():
        print("commit")
        if created and instance.file and os.path.isfile(instance.file.file.path):
            from core.tasks import async_seed_csv_file
            worker = async_seed_csv_file.delay(instance.dataset.id, instance.file.id, instance.id)
            instance.task_id = worker.idea
            instance.save()
        elif created:
            raise Exception("File not present")
    transaction.on_commit(lambda: on_commit())


@receiver(models.signals.post_save, sender=TaskResult)
def add_task_result_to_update(sender, instance, created, **kwargs):
    def on_commit():
        if created and instance.task_name == 'core.tasks.async_seed_csv_file':
            u = Update.objects.get(task_id=instance.task_id)
            u.task_result = instance
            u.save()

    transaction.on_commit(lambda: on_commit())
