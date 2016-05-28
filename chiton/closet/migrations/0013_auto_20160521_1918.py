# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-05-21 19:18
from __future__ import unicode_literals

import autoslug.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chiton_closet', '0012_size_is_plus_sized'),
    ]

    operations = [
        migrations.RenameField(
            model_name='size',
            old_name='size_lower',
            new_name='range_lower',
        ),
        migrations.RenameField(
            model_name='size',
            old_name='size_upper',
            new_name='range_upper',
        ),
        migrations.RemoveField(
            model_name='size',
            name='is_petite',
        ),
        migrations.RemoveField(
            model_name='size',
            name='is_tall',
        ),
        migrations.AlterField(
            model_name='size',
            name='slug',
            field=autoslug.fields.AutoSlugField(max_length=255, unique=True, verbose_name='slug'),
        ),
    ]