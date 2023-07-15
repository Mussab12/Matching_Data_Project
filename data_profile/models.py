from datetime import datetime

from django.db import models
from vihoapp.models import User


class DataProfile(models.Model):
    """
        Model for data profile
            @table - vihoapp_profile
    """
    status_choice = (
        ("PENDING", "PENDING"),
        ("DOING", "DOING"),
        ("DONE", "DONE")
    )
    name = models.CharField(max_length=200)
    data_source = models.CharField(max_length=200)
    email_address = models.CharField(max_length=255)
    details = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=255, choices=status_choice, default="PENDING")
    data_source_output = models.CharField(max_length=255, null=False, default="output")

    class Meta:
        db_table = "vihoapp_profile"


class DataPattern(models.Model):
    """
        Model for data patterns
            @table - vihoapp_patterns
    """
    name = models.CharField(max_length=255, null=False)
    type = models.CharField(max_length=200, null=False)
    pattern = models.TextField(null=False)
    selected = models.BooleanField(default=False)

    class Meta:
        db_table = "vihoapp_patterns"


class DataProfileHistory(models.Model):
    """
        Model for data history
            @table - vihoapp_profile_history
    """
    profile_id = models.IntegerField(null=False)
    profile_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    profile_result = models.TextField(null=False)
    profile_time = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=datetime.now)

    class Meta:
        db_table = "vihoapp_profile_history"
