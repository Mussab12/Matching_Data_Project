# Generated by Django 4.0 on 2023-07-17 20:18

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('vihoapp', '0034_alter_datafile_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datafile',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2023, 7, 17, 20, 18, 35, 214766, tzinfo=utc)),
        ),
    ]
