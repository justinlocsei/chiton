# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-02 12:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chiton_wintour', '0012_auto_20160902_1157'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='encrypted_email',
            field=models.TextField(default='', verbose_name='encrypted email'),
            preserve_default=False,
        ),
    ]