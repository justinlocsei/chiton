# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-06-04 01:50
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chiton_rack', '0011_auto_20160604_0134'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='affiliateitem',
            unique_together=set([('guid', 'network')]),
        ),
    ]
