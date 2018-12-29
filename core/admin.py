from django.contrib import admin
from django.db.models import Count
from django.http import HttpResponseRedirect
from .models import Dataset, DataFile, Update
from app.admin.mixins import admin_changelist_link, admin_link
from core.tasks import async_download_file

import requests
import tempfile
import re

from django.core import files


class DatasetAdmin(admin.ModelAdmin):
    def response_change(self, request, obj):
        if "_download-file" in request.POST:
            async_download_file()
            self.message_user(request, "This file is now downloading.")
            return HttpResponseRedirect(".")
        return super().response_change(request, obj)

    @admin_changelist_link('datafile_set', ('DataFiles'), query_string=lambda c: 'dataset={}'.format(c.pk))
    def datafiles_link(self, updates):
        return ('View DateFiles')

    @admin_changelist_link('update_set', ('Updates'), query_string=lambda c: 'dataset={}'.format(c.pk))
    def updates_link(self, updates):
        return ('View Updates')

    def data_files_count(self, inst):
        return inst.datafile_set.count()

    def updates_count(self, inst):
        return inst.update_set.count()

    def download_file(self, request, queryset):
        for object in queryset:
            if object.download_endpoint:
                file_request = requests.get(object.download_endpoint, stream=True)
                # Was the request OK?
                if file_request.status_code != requests.codes.ok:
                    # Nope, error handling, skip file etc etc etc
                    continue

                # get filename
                if 'content-disposition' in file_request.headers:
                    file_name = re.findall("filename=(.+)", file_request.headers['content-disposition'])[0]
                else:
                    file_name = object.download_endpoint.split('/')[-1]
                print(file_name)

                # Create a temporary file
                lf = tempfile.NamedTemporaryFile()

                # Read the streamed file in sections
                downloaded = 0
                for block in file_request.iter_content(1024 * 8):
                    downloaded += len(block)
                    print("{0} MB".format(downloaded / 1000000))
                    # If no more file then stop
                    if not block:
                        break

                    # Write file block to temporary file
                    lf.write(block)

                data_file = DataFile(dataset=object)
                data_file.file.save(file_name, files.File(lf))

                self.message_user(request, "All data successfully downloaded.")
            else:
                raise Exception("No download endpoint set. Cannot download.")

    download_file.short_description = "Download the latest data"

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    list_display = ['name', 'model_name', 'download_endpoint',
                    'updates_count', 'updates_link', 'data_files_count', 'datafiles_link']
    Dataset.objects.prefetch_related('update')
    Dataset.objects.prefetch_related('datafile')
    ordering = ['name']
    actions = []


class DataFileAdmin(admin.ModelAdmin):
    @admin_link('dataset', ('Dataset'), query_string=lambda c: 'id={}'.format(c.dataset.pk))
    def dataset_link(self, dataset):
        return dataset

    def has_delete_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return False

    list_display = ['id', 'dataset_link', 'uploaded_date', 'file']
    ordering = ['-uploaded_date']
    actions = []


class UpdateAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin_link('dataset', ('Dataset'), query_string=lambda c: 'id={}'.format(c.dataset.pk))
    def dataset_link(self, dataset):
        return dataset

    @admin_link('file', ('File'), query_string=lambda c: 'id={}'.format(c.file.pk))
    def file_link(self, datafile):
        return datafile.file.name

    @admin_link('task_result', ('Task Result'))
    def task_result_link(self, task_result):
        return task_result.status

    list_display = ['id', 'dataset_link', 'model_name', 'file_link',
                    'rows_updated', 'rows_created', 'created_date', 'completed_date',  'task_id', 'task_result_link']

    list_select_related = (
        'task_result',
    )

    ordering = ['-created_date']
    actions = []


admin.site.register(Dataset, DatasetAdmin)
admin.site.register(DataFile, DataFileAdmin)
admin.site.register(Update, UpdateAdmin)
