# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-05-09 00:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chiton_rack', '0003_stockrecord'),
    ]

    operations = [
        migrations.AddField(
            model_name='affiliateitem',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name='price'),
        ),
    ]