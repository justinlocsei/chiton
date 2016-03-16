# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-16 00:20
from __future__ import unicode_literals

import autoslug.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Basic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='name')),
                ('slug', autoslug.fields.AutoSlugField(editable=False, max_length=255, populate_from='name', unique=True, verbose_name='slug')),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'basic',
                'verbose_name_plural': 'basics',
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='name')),
                ('slug', autoslug.fields.AutoSlugField(editable=False, max_length=255, populate_from='name', unique=True, verbose_name='slug')),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'category',
                'verbose_name_plural': 'categories',
            },
        ),
        migrations.CreateModel(
            name='Formality',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255, verbose_name='name')),
                ('slug', autoslug.fields.AutoSlugField(editable=False, max_length=255, populate_from='name', unique=True, verbose_name='slug')),
                ('position', models.PositiveSmallIntegerField(default=0, verbose_name='position')),
            ],
            options={
                'ordering': ('position',),
                'verbose_name': 'level of formality',
                'verbose_name_plural': 'levels of formality',
            },
        ),
        migrations.CreateModel(
            name='Propriety',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('importance', models.CharField(choices=[('mildly', 'Not that important'), ('somewhat', 'Somewhat important'), ('very', 'Very important'), ('always', 'Always important')], max_length=25, verbose_name='importance')),
                ('basic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chiton_runway.Basic', verbose_name='basic')),
                ('formality', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chiton_runway.Formality', verbose_name='level of formality')),
            ],
            options={
                'verbose_name': 'propriety',
                'verbose_name_plural': 'proprieties',
            },
        ),
        migrations.CreateModel(
            name='Style',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='name')),
                ('slug', autoslug.fields.AutoSlugField(editable=False, max_length=255, populate_from='name', unique=True, verbose_name='slug')),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'style',
                'verbose_name_plural': 'styles',
            },
        ),
        migrations.AddField(
            model_name='basic',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chiton_runway.Category', verbose_name='category'),
        ),
        migrations.AddField(
            model_name='basic',
            name='formalities',
            field=models.ManyToManyField(through='chiton_runway.Propriety', to='chiton_runway.Formality', verbose_name='levels of formality'),
        ),
    ]
