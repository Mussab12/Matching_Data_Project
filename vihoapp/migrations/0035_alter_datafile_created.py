<<<<<<< HEAD
# Generated by Django 4.0 on 2023-07-17 20:18
=======
# Generated by Django 4.0 on 2023-07-21 10:15
>>>>>>> master

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
<<<<<<< HEAD
            field=models.DateTimeField(default=datetime.datetime(2023, 7, 17, 20, 18, 35, 214766, tzinfo=utc)),
=======
            field=models.DateTimeField(default=datetime.datetime(2023, 7, 21, 10, 15, 46, 900557, tzinfo=utc)),
>>>>>>> master
        ),
    ]