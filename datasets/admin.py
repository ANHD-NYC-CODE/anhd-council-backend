from django.contrib import admin
from datasets.models import Council, Community, Property, Building, AddressRecord


admin.site.register(Council)
admin.site.register(Community)
admin.site.register(Property)
admin.site.register(Building)
admin.site.register(AddressRecord)
