<<<<<<< HEAD
# Generated by Django 4.0 on 2023-07-18 20:58
=======
# Generated by Django 4.0 on 2023-07-21 10:39
>>>>>>> master

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('vihoapp', '0041_alter_datafile_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datafile',
            name='created',
<<<<<<< HEAD
            field=models.DateTimeField(default=datetime.datetime(2023, 7, 18, 20, 58, 29, 435315, tzinfo=utc)),
=======
            field=models.DateTimeField(default=datetime.datetime(2023, 7, 21, 10, 39, 54, 567733, tzinfo=utc)),
>>>>>>> master
        ),
    ]
