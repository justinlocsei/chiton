# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-05-05 23:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chiton_runway', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='propriety',
            name='importance',
            field=models.CharField(choices=[('not', 'Not important'), ('mildly', 'Not that important'), ('somewhat', 'Somewhat important'), ('very', 'Very important'), ('always', 'Always important')], max_length=25, verbose_name='importance'),
        ),
    ]
