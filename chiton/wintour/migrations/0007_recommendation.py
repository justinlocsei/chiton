# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-06-17 03:21
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chiton_wintour', '0006_wardrobeprofile_sizes'),
    ]

    operations = [
        migrations.CreateModel(
            name='Recommendation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile', django.contrib.postgres.fields.jsonb.JSONField(verbose_name='The profile data')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
            ],
            options={
                'verbose_name': 'recommendation',
                'ordering': ('-created_at',),
                'verbose_name_plural': 'recommendations',
            },
        ),
    ]