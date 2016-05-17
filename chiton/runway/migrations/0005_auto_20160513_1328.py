# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-05-13 13:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chiton_closet', '0007_auto_20160508_1729'),
        ('chiton_runway', '0004_basic_colors'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='basic',
            name='colors',
        ),
        migrations.AddField(
            model_name='basic',
            name='primary_color',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='primary_for', to='chiton_closet.Color', verbose_name='primary color'),
        ),
        migrations.AddField(
            model_name='basic',
            name='secondary_colors',
            field=models.ManyToManyField(related_name='secondary_for', to='chiton_closet.Color', verbose_name='secondary colors'),
        ),
    ]