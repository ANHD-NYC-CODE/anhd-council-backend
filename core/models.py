from django.utils import timezone
from django.db import models, transaction
from django.dispatch import receiver
from django.apps import apps
from django.conf import settings
from django_celery_results.models import TaskResult
from datasets import models as dataset_models

import time
import datetime
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
        return getattr(dataset_models, self.model_name).transform_self(file_path)

    def seed_dataset(self, **kwargs):
        return getattr(dataset_models, self.model_name).seed_or_update_self(**kwargs)

    def latest_update(self):
        try:
            latest = self.update_set.filter(task_result__status="SUCCESS").latest('created_date')
        except Exception as e:
            latest = None
        return latest

    def latest_file(self):
        return self.datafile_set.latest('uploaded_date')

    def __str__(self):
        return self.name


def construct_directory_path(instance, filename):
    split_filename = filename.split('.')
    name = split_filename[0]
    extension = split_filename[1]
    return '{0}/{1}'.format(settings.MEDIA_ROOT, "{0}__{1}.{2}".format(name, datetime.datetime.now().strftime("%m%d%Y%H%M%S"), extension))


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
        return str(self.id)


@receiver(models.signals.post_save, sender=Update)
def auto_batch_insert_from_file_on_create(sender, instance, created, **kwargs):
    """
    Seeds file in DB
    when corresponding `Update` object is created.
    """

    def on_commit():
        print("commit")
        if created and instance.file and os.path.isfile(instance.file.file.path):
            from core.tasks import async_seed_file
            # worker = async_seed_file.delay(instance.dataset.id, instance.file.id, instance.id)
            # instance.task_id = worker.id
            async_seed_file.delay(instance.dataset.id, instance.file.id, instance.id)
            instance.save()
        elif created:
            raise Exception("File not present")
    transaction.on_commit(lambda: on_commit())


@receiver(models.signals.post_save, sender=TaskResult)
def add_task_result_to_update(sender, instance, created, **kwargs):
    def on_commit():
        if created:
            u = Update.objects.filter(task_id=instance.task_id).first()
            if u:
                u.completed_date = timezone.now
                u.task_result = instance
                u.save()

    transaction.on_commit(lambda: on_commit())
