<<<<<<< HEAD
# Generated by Django 4.0 on 2023-07-17 21:01
=======
# Generated by Django 4.0 on 2023-07-21 10:17
>>>>>>> master

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('vihoapp', '0036_alter_datafile_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datafile',
            name='created',
<<<<<<< HEAD
            field=models.DateTimeField(default=datetime.datetime(2023, 7, 17, 21, 1, 44, 75968, tzinfo=utc)),
=======
            field=models.DateTimeField(default=datetime.datetime(2023, 7, 21, 10, 17, 18, 595286, tzinfo=utc)),
>>>>>>> master
        ),
    ]
