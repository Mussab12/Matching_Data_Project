# Generated by Django 4.0 on 2023-07-07 14:27

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('vihoapp', '0008_alter_datafile_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datafile',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2023, 7, 7, 14, 27, 56, 288732, tzinfo=utc)),
        ),
    ]
