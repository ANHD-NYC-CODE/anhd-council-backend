from django.contrib import admin
from django.db.models import Count
from .models import Dataset, DataFile, Update
import requests
import tempfile
import re

from django.core import files


class DatasetAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super(DatasetAdmin, self).get_queryset(request)
        return qs.annotate(data_files_count=Count('datafile'))

    def data_files_count(self, inst):
        return inst.data_files_count

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

    list_display = ['name', 'model_name', 'download_endpoint', 'data_files_count']
    ordering = ['name']
    actions = []


class DataFileAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return False

    list_display = ['dataset', 'uploaded_date', 'file']
    ordering = ['uploaded_date']
    actions = []


class UpdateAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    list_display = ['dataset', 'update_date', 'model_name', 'file']
    ordering = ['update_date']
    actions = []


admin.site.register(Dataset, DatasetAdmin)
admin.site.register(DataFile, DataFileAdmin)
admin.site.register(Update, UpdateAdmin)
