from django.db import models
from datetime import date
from django.contrib.postgres.fields import JSONField

# Create your models here.


class exceldata(models.Model):
    company_name = models.CharField(max_length=255, null=False)
    Industry = models.CharField(max_length=255, null=False)


class CustomerMaster(models.Model):
    data1 = models.JSONField()

    relationship = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL)  # to make data1->data1 relation

    class Meta:
        verbose_name = "Customer Master"


class NewProsectRecords(models.Model):
    data2 = models.JSONField()

    class Meta:
        verbose_name = "New Prospect Records"


class MatchingConfig(models.Model):
    matchdata = models.JSONField()
