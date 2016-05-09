# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-05-08 17:06
from __future__ import unicode_literals

import autoslug.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chiton_closet', '0005_garment_is_featured'),
    ]

    operations = [
        migrations.CreateModel(
            name='Color',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255, verbose_name='name')),
                ('slug', autoslug.fields.AutoSlugField(editable=False, max_length=255, populate_from='name', unique=True, verbose_name='slug')),
            ],
            options={
                'verbose_name_plural': 'colors',
                'ordering': ('name',),
                'verbose_name': 'color',
            },
        ),
    ]