# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-22 14:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('iati_codelists', '0001_initial'),
        ('iati_organisation', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='organisation',
            name='type',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='iati_codelists.OrganisationType'),
        ),
    ]
