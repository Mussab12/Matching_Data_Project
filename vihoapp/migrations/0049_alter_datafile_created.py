# Generated by Django 4.0 on 2023-07-19 09:49

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('vihoapp', '0048_alter_datafile_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datafile',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2023, 7, 19, 9, 49, 38, 647431, tzinfo=utc)),
        ),
    ]
