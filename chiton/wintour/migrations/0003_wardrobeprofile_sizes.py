# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-05-20 01:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chiton_closet', '0010_auto_20160520_0104'),
        ('chiton_wintour', '0002_auto_20160505_2353'),
    ]

    operations = [
        migrations.AddField(
            model_name='wardrobeprofile',
            name='sizes',
            field=models.ManyToManyField(to='chiton_closet.Size', verbose_name='sizes'),
        ),
    ]
