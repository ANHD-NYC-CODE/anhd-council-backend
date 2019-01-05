from django.contrib import admin
from .models import Council, Building, HPDViolation


admin.site.register(Council)
admin.site.register(Building)
admin.site.register(HPDViolation)

# Register your models here.
