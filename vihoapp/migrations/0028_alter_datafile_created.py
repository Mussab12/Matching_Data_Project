# Generated by Django 4.0 on 2023-07-14 22:50

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('vihoapp', '0027_alter_datafile_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datafile',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2023, 7, 14, 22, 50, 35, 255739, tzinfo=utc)),
        ),
    ]
