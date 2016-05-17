# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-05-16 17:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chiton_closet', '0008_auto_20160516_1726'),
    ]

    operations = [
        migrations.AlterField(
            model_name='size',
            name='size_lower',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='lower numeric size'),
        ),
        migrations.AlterField(
            model_name='size',
            name='size_upper',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='upper numeric size'),
        )
    ]