<<<<<<< HEAD
# Generated by Django 4.0 on 2023-07-17 20:25
=======
# Generated by Django 4.0 on 2023-07-21 10:16
>>>>>>> master

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('vihoapp', '0035_alter_datafile_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datafile',
            name='created',
<<<<<<< HEAD
            field=models.DateTimeField(default=datetime.datetime(2023, 7, 17, 20, 25, 41, 921067, tzinfo=utc)),
=======
            field=models.DateTimeField(default=datetime.datetime(2023, 7, 21, 10, 16, 26, 601343, tzinfo=utc)),
>>>>>>> master
        ),
    ]
