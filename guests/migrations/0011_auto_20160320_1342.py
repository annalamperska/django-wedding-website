# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-03-20 13:42
from __future__ import unicode_literals

from django.db import migrations, models
import guests.models


class Migration(migrations.Migration):

    dependencies = [
        ('guests', '0010_auto_20160320_1338'),
    ]

    operations = [
        migrations.AlterField(
            model_name='party',
            name='invitation_id',
            field=models.CharField(db_index=True, default=None, max_length=32),
        ),
    ]
