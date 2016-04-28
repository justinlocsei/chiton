# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-28 23:43
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chiton_rack', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='affiliateitem',
            name='garment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='affiliate_items', to='chiton_closet.Garment', verbose_name='garment'),
        ),
    ]
