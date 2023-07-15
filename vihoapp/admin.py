from import_export.admin import ImportExportMixin
from django.contrib import admin
from .models import User
from . import models
from .models import Datafile
# Register your models here.
admin.site.register(User)
admin.site.register(models.Task)

class DatafileAdmin(ImportExportMixin, admin.ModelAdmin):
    ...
    #list_display = ['name', 'description', 'due_date', 'is_complete']

admin.site.register(Datafile, DatafileAdmin)