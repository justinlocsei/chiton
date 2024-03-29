# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-05-08 17:29
from __future__ import unicode_literals

import autoslug.fields
import chiton.closet.models # noqa
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chiton_closet', '0006_color'),
    ]

    operations = [
        migrations.CreateModel(
            name='Size',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('base', models.CharField(choices=[('xxs', 'XXS'), ('xs', 'XS'), ('s', 'S'), ('m', 'M'), ('l', 'L'), ('xl', 'XL'), ('xxl', 'XXL'), ('plus1', 'Plus 1X'), ('plus2', 'Plus 2X'), ('plus3', 'Plus 3X'), ('plus4', 'Plus 4X'), ('plus5', 'Plus 5X')], max_length=15, verbose_name='base size')),
                ('slug', autoslug.fields.AutoSlugField(editable=False, max_length=255, unique=True, verbose_name='slug')),
                ('size_lower', models.PositiveSmallIntegerField(verbose_name='lower numeric size')),
                ('size_upper', models.PositiveSmallIntegerField(verbose_name='upper numeric size')),
                ('is_petite', models.BooleanField(default=False, verbose_name='is petite')),
                ('is_tall', models.BooleanField(default=False, verbose_name='is tall')),
                ('position', models.PositiveSmallIntegerField(default=0, verbose_name='position')),
            ],
            options={
                'ordering': ('position',),
                'verbose_name': 'size',
                'verbose_name_plural': 'sizes',
            },
        ),
        migrations.AlterUniqueTogether(
            name='size',
            unique_together=set([('size_lower', 'size_upper', 'is_tall', 'is_petite')]),
        ),
    ]
