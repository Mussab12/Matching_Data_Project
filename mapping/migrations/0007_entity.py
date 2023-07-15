# Generated by Django 4.0 on 2023-07-07 11:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mapping', '0006_rename_mappingrecode_mappingrecord'),
    ]

    operations = [
        migrations.CreateModel(
            name='Entity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entity_id', models.CharField(max_length=250)),
                ('entity_name', models.TextField(blank=True, null=True)),
                ('data_source', models.TextField(blank=True, null=True)),
                ('record_id', models.CharField(max_length=250)),
                ('entity_type', models.TextField(blank=True, null=True)),
                ('internal_id', models.CharField(max_length=250)),
                ('entity_key', models.TextField(blank=True, null=True)),
                ('entity_desc', models.TextField(blank=True, null=True)),
                ('match_key', models.TextField(blank=True, null=True)),
                ('match_level', models.CharField(max_length=250)),
                ('match_level_code', models.TextField(blank=True, null=True)),
                ('errule_code', models.TextField(blank=True, null=True)),
                ('last_seen_dt', models.TextField(blank=True, null=True)),
                ('lens_code', models.TextField(blank=True, null=True)),
                ('name_data', models.TextField(blank=True, null=True)),
                ('attribute_data', models.TextField(blank=True, null=True)),
                ('identifier_data', models.TextField(blank=True, null=True)),
                ('address_data', models.TextField(blank=True, null=True)),
                ('phone_data', models.TextField(blank=True, null=True)),
                ('relationship_data', models.TextField(blank=True, null=True)),
                ('entity_data', models.TextField(blank=True, null=True)),
                ('other_data', models.TextField(blank=True, null=True)),
                ('user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, to=settings.AUTH_USER_MODEL, verbose_name='id')),
            ],
            options={
                'db_table': 'vihoapp_entity',
            },
        ),
    ]
