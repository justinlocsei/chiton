# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-11 19:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chiton_rack', '0014_affiliateitem_has_detailed_stock'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productimage',
            name='url',
        ),
        migrations.AddField(
            model_name='productimage',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='products', verbose_name='file'),
        ),
    ]