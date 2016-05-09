# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-28 23:50
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('chiton_closet', '0003_garment_care'),
    ]

    operations = [
        migrations.AddField(
            model_name='garment',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2016, 4, 28, 23, 50, 0, 231995, tzinfo=utc), verbose_name='created at'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='garment',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, default=datetime.datetime(2016, 4, 28, 23, 50, 4, 497984, tzinfo=utc), verbose_name='updated at'),
            preserve_default=False,
        ),
    ]