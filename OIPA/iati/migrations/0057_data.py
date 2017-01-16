# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-10-27 01:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('iati', '0057_add'),
    ]


    def add_dataset(apps, schema_editor):
        try: # don't run on first migration
            Activity = apps.get_model('iati', 'Activity')
            Dataset = apps.get_model('iati', 'Dataset')
        except:
            return

        for d in Dataset.objects.all():
            Activity.objects.filter(xml_source_ref=d.name).update(dataset=d)


    operations = [
        migrations.RunPython(add_dataset),
    ]