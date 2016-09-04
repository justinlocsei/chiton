# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-04 00:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chiton_wintour', '0014_person_joined'),
    ]

    operations = [
        migrations.AddField(
            model_name='wardrobeprofile',
            name='recommendation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='chiton_wintour.Recommendation', verbose_name='recommendation'),
        ),
    ]
