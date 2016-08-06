# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-02 10:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chiton_runway', '0011_auto_20160526_2345'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ('position',), 'verbose_name': 'category', 'verbose_name_plural': 'categories'},
        ),
        migrations.AddField(
            model_name='category',
            name='position',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='position'),
        ),
    ]