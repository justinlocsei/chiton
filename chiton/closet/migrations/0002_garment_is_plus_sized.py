# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-16 00:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chiton_closet', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='garment',
            name='is_plus_sized',
            field=models.BooleanField(default=False, verbose_name='is for plus-sized women'),
        ),
    ]
