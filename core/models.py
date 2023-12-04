from django.utils import timezone
from django.db import models, transaction
from django.dispatch import receiver
from django.apps import apps
from django.conf import settings
from django_celery_results.models import TaskResult
from core.tasks import async_seed_file, async_seed_table, async_send_update_success_mail, async_download_and_update
from datasets import models as ds


import time
import datetime
import os
import itertools
import datetime
from django.utils.timezone import make_aware
import logging

logger = logging.getLogger('app')


class Dataset(models.Model):
    UPDATE_SCHEDULE_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('when needed', 'When Needed'),
    ]

    name = models.CharField(unique=True, max_length=255,
                            blank=False, null=False)
    model_name = models.CharField(
        unique=True, max_length=255, blank=False, null=False)
    automated = models.BooleanField(blank=True, null=True)
    update_instructions = models.TextField(blank=True, null=True)
    download_endpoint = models.TextField(blank=True, null=True)
    api_last_updated = models.DateTimeField(blank=True, null=True)
    records_start = models.DateField(blank=True, null=True)
    records_end = models.DateField(blank=True, null=True)
    update_schedule = models.CharField(
        max_length=255, choices=UPDATE_SCHEDULE_CHOICES, blank=True, null=True)

    @classmethod
    def annotate_properties_all(cls):
        current_model_name = None  # Initialize variable to keep track of the current model name
        try:
            for model_name in settings.ANNOTATED_DATASETS:
                current_model_name = model_name  # Update the current model name
                if model_name == 'AcrisRealMaster':
                    model_name = 'AcrisRealLegal'
                dataset = cls.objects.get(model_name=model_name)
                dataset.model().annotate_properties()
        except Exception as e:
            if current_model_name:
                logger.error(
                    f'Error during task for model_name "{current_model_name}": {e}')
            else:
                logger.error(f'Error during task: {e}')

    def model(self):
        return getattr(ds, self.model_name)

    def download(self, endpoint=None, file_name=None):
        return getattr(ds, self.model_name).download(endpoint=endpoint, file_name=file_name)

    def update(self, file=None):
        return Update.objects.create(dataset=self, file=file)

    def needs_update(self):
        return self.api_last_updated != getattr(ds, self.model_name).fetch_last_updated()

    def update_records_range(self):
        dataset = getattr(ds, self.model_name)

        def get_earliest_date():
            if hasattr(dataset, 'EARLIEST_RECORD'):
                return dataset.EARLIEST_RECORD
            else:
                return '1950-01-01'

        if hasattr(dataset, 'QUERY_DATE_KEY'):
            try:
                query = dataset.objects.filter(
                    **{
                        "{}__isnull".format(dataset.QUERY_DATE_KEY): False,
                        "{}__gte".format(dataset.QUERY_DATE_KEY): get_earliest_date(),
                        "{}__lte".format(dataset.QUERY_DATE_KEY): datetime.datetime.now()
                    })
                self.records_start = getattr(query.earliest(
                    dataset.QUERY_DATE_KEY), dataset.QUERY_DATE_KEY)
                self.records_end = getattr(query.latest(
                    dataset.QUERY_DATE_KEY), dataset.QUERY_DATE_KEY)
                self.save()
            except Exception as e:
                print(e)
                logger.warning(e)

    def check_api_for_update(self):
        self.api_last_updated = getattr(
            ds, self.model_name).fetch_last_updated()
        if self.api_last_updated:
            self.save()

    def check_api_for_update_and_update(self):
        if self.api_last_updated:
            api_last_updated = getattr(
                ds, self.model_name).fetch_last_updated()

            if not api_last_updated or api_last_updated.replace(tzinfo=timezone.utc) > self.api_last_updated.replace(tzinfo=timezone.utc):
                self.model().create_async_update_worker()
            else:
                logger.debug('Dataset {} is up to date.'.format(self.name))
        else:
            self.model().create_async_update_worker()

    def seed_dataset(self, **kwargs):
        getattr(ds, self.model_name).seed_or_update_self(**kwargs)
        self.delete_old_files()

    def split_seed_dataset(self, **kwargs):
        getattr(ds, self.model_name).split_seed_or_update_self(**kwargs)

    def latest_update(self):
        from core.models import Dataset
        # Make sure to prefetch_related('update_set')
        try:
            update_source = Dataset.objects.get(
                model_name=self.model().UPDATE_SOURCE) if hasattr(self.model(), 'UPDATE_SOURCE') else self
            latest = update_source.update_set.filter(
                task_result__status="SUCCESS").latest('created_date')
        except Exception as e:
            logger.warning(e)
            latest = None
        return latest

    def latest_file(self):
        # Make sure to prefetch_related('datefile_set')
        try:
            return self.datafile_set.latest('uploaded_date')
        except Exception as e:
            return None

    def second_latest_file(self):
        try:
            return self.datafile_set.order_by('-uploaded_date').all()[1]
        except Exception as e:
            return None

    def latest_version(self):
        latest_file = self.latest_file()
        if latest_file:
            return latest_file.version
        else:
            return None

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
    return '{0}/{1}'.format(settings.MEDIA_ROOT, "{0}__{1}.{2}".format(name, make_aware(datetime.datetime.now()).strftime("%m%d%Y%H%M%S"), extension))


class DataFile(models.Model):
    file = models.FileField(upload_to=construct_directory_path)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    uploaded_date = models.DateTimeField(default=timezone.now)
    version = models.TextField(blank=True, null=True)

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
            try:
                os.remove(instance.file.path)
            except Exception as e:
                logger.warning(e)


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
    # TODO: change to make_aware(datetime.now())
    created_date = models.DateTimeField(default=timezone.now)
    completed_date = models.DateTimeField(blank=True, null=True)
    task_id = models.CharField(max_length=255, blank=True, null=True)
    task_result = models.ForeignKey(
        TaskResult, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return str(self.id)

    @classmethod
    def ensure_update_task_results(self):
        for update in self.objects.filter(task_result__isnull=True):
            try:
                task_result = TaskResult.objects.get(task_id=update.task_id)
                update.task_result = task_result
                update.completed_date = task_result.date_done
                update.save()
            except Exception as e:
                logger.debug(
                    'Task result with task_id {} not found'.format(update.task_id))


@receiver(models.signals.post_save, sender=Update)
def auto_seed_on_create(sender, instance, created, **kwargs):
    """
    Seeds file in DB
    when corresponding `Update` object is created.
    """

    def on_commit():
        if created == True:
            if not instance.dataset and not instance.file:
                raise Exception("File and dataset not present")
            elif not instance.dataset:
                instance.dataset = instance.file.dataset

            logger.debug(
                "Creating worker task for update {}".format(instance.id))
            if instance.file:
                worker = async_seed_file.apply_async(args=[instance.file.file.path, instance.id], kwargs={
                    'dataset_id': instance.dataset.id}, countdown=2)
            else:
                worker = async_seed_table.apply_async(
                    args=[instance.id], countdown=2)

            instance.task_id = worker.id
            logger.debug("Linking Worker {} to update {}".format(
                worker.id, instance.id))
            instance.save()
    transaction.on_commit(lambda: on_commit())


@receiver(models.signals.post_save, sender=TaskResult)
def add_task_result_to_update(sender, instance, created, **kwargs):
    def on_commit():
        try:
            u = Update.objects.get(task_id=instance.task_id)
            if u:
                u.task_result = instance
                u.completed_date = instance.date_done
                u.save()
                u.dataset.check_api_for_update()  # update dataset update time after success
                # update records start / records end after success
                u.dataset.update_records_range()
                # async_send_update_success_mail.delay(u.id) # too many emails, too annoying

        except Exception as e:
            logger.warning(
                "TaskResult {} not synced to Update".format(instance.id))

    transaction.on_commit(lambda: on_commit())


class UserMessage(models.Model):
    STATUS_CHOICES = (
        ('reported', 'Reported'),
        ('duplicate', 'Duplicate'),
        ('investigating', 'Investigating'),
        ('fixed', 'Fixed'),
        ('unable', 'Unable to reproduce'),
    )

    from_email = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    status = models.TextField(
        blank=True, null=True, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])
    date_created = models.DateTimeField(
        auto_now_add=True, blank=True, null=True)


@receiver(models.signals.post_save, sender=UserMessage)
def send_user_message_email_on_save(sender, instance, created, **kwargs):
    from app.tasks import async_send_user_message_email

    def on_commit():
        if created == True:
            async_send_user_message_email.delay(instance.id)

    transaction.on_commit(lambda: on_commit())
