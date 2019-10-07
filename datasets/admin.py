from django.contrib import admin
from datasets.models import Council, Community, ZipCode, StateAssembly, StateSenate, Property, Building, AddressRecord


admin.site.register(Council)
admin.site.register(Community)
admin.site.register(StateAssembly)
admin.site.register(StateSenate)
admin.site.register(ZipCode)
admin.site.register(Property)
admin.site.register(Building)
admin.site.register(AddressRecord)
