from django.db import models
from vihoapp.models import User
# Create your models here.
   
# Category for mapping
class Category(models.Model):
    name = models.CharField(max_length=250)

    class Meta:
        db_table = "vihoapp_category"

    def get_data(self):
        return {
            'id': self.id,
            'name': self.name
        }
    
#DataSource for mapping
class DataSource(models.Model):
    name = models.CharField(max_length=250)

    class Meta:
        db_table = "vihoapp_datasource"

    def get_data(self):
        return {
            'id': self.id,
            'name': self.name
        }

#Mapping list for mapping
class MappingList(models.Model):
    senzing_map_name = models.CharField(max_length=250)
    display_name = models.CharField(max_length=250)
    category = models.ForeignKey(Category, default=1, verbose_name="id", on_delete=models.SET_DEFAULT)

    class Meta:
        db_table = "vihoapp_mappinglist"
    
    def get_data(self):
        return {
            'id': self.id,
            'category_id': self.category.id,
            'category_name': self.category.name,
            'name': self.senzing_map_name,
            'display_name': self.display_name
        }

#Recode for Mapping
class MappingRecord(models.Model):
    data = models.TextField(blank=True, null=True)
    datasource = models.ForeignKey(DataSource, default=1, verbose_name="id", on_delete = models.SET_DEFAULT)
    user = models.ForeignKey(User, default=1, verbose_name="id", on_delete = models.SET_DEFAULT)

    class Meta:
        db_table = "vihoapp_mappingrecord"

    def get_data(self):
        return {
            'RECORD_ID': self.id,
            'DataSource_ID': self.datasource.id,
            'DataSource': self.datasource.name,
            'data': self.data
        }

#Entity after senzing
class Entity(models.Model):
    entity_id = models.CharField(max_length=250)
    entity_name = models.TextField(blank=True, null=True)
    data_source = models.TextField(blank=True, null=True)
    record_id = models.CharField(max_length=250)
    entity_type = models.TextField(blank=True, null=True)
    internal_id = models.CharField(max_length=250)
    entity_key = models.TextField(blank=True, null=True)
    entity_desc = models.TextField(blank=True, null=True)
    match_key = models.TextField(blank=True, null=True)
    match_level = models.CharField(max_length=250)
    match_level_code = models.TextField(blank=True, null=True)
    errule_code = models.TextField(blank=True, null=True)
    last_seen_dt = models.TextField(blank=True, null=True)
    lens_code = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, default=1, verbose_name="id", on_delete = models.SET_DEFAULT)
    name_data = models.TextField(blank=True, null=True)
    attribute_data = models.TextField(blank=True, null=True)
    identifier_data = models.TextField(blank=True, null=True)
    address_data = models.TextField(blank=True, null=True)
    phone_data = models.TextField(blank=True, null=True)
    relationship_data = models.TextField(blank=True, null=True)
    entity_data = models.TextField(blank=True, null=True)
    other_data = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = "vihoapp_entity"