# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-05-13 13:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chiton_runway', '0005_auto_20160513_1328'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basic',
            name='secondary_colors',
            field=models.ManyToManyField(blank=True, null=True, related_name='secondary_for', to='chiton_closet.Color', verbose_name='secondary colors'),
        ),
    ]
