# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-05-09 00:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chiton_closet', '0007_auto_20160508_1729'),
        ('chiton_rack', '0002_auto_20160427_2344'),
    ]

    operations = [
        migrations.CreateModel(
            name='StockRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_available', models.BooleanField(default=False, verbose_name='is available')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stock_records', to='chiton_rack.AffiliateItem', verbose_name='affiliate item')),
                ('size', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chiton_closet.Size', verbose_name='size')),
            ],
            options={
                'verbose_name_plural': 'stock records',
                'verbose_name': 'stock record',
            },
        ),
    ]
