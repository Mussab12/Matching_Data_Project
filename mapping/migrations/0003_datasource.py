# Generated by Django 4.0 on 2023-05-22 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mapping', '0002_rename_category_id_mappinglist_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataSource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
            ],
            options={
                'db_table': 'vihoapp_datasource',
            },
        ),
    ]