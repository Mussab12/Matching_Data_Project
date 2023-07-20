from django.db import models
from datetime import date
from django.contrib.postgres.fields import JSONField

# Create your models here.


class exceldata(models.Model):
    company_name = models.CharField(max_length=255, null=False)
    Industry = models.CharField(max_length=255, null=False)


class CustomerMaster(models.Model):
    # Use a JSONField to store dynamic data

    data1 = models.JSONField()

    class Meta:
        verbose_name = "Customer Master"


class Relationship(models.Model):
    from_data = models.ForeignKey(
        CustomerMaster, related_name='from_relationships', on_delete=models.CASCADE)
    to_data = models.ManyToManyField(
        CustomerMaster, related_name='to_relationships')


class NewProsectRecords(models.Model):
    data2 = models.JSONField()

    class Meta:
        verbose_name = "New Prospect Records"


class MatchingConfig(models.Model):
    matchdata = models.JSONField()
