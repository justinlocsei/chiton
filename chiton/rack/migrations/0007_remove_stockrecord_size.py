# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-05-22 00:39
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chiton_rack', '0006_remove_productimage_item'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stockrecord',
            name='size',
        ),
    ]
