# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-09 00:25
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AffiliateItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.TextField(verbose_name='URL')),
                ('name', models.CharField(db_index=True, max_length=255, verbose_name='name')),
                ('guid', models.CharField(max_length=255, verbose_name='GUID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='created at')),
            ],
            options={
                'verbose_name_plural': 'affiliate items',
                'verbose_name': 'affiliate item',
            },
        ),
        migrations.CreateModel(
            name='AffiliateNetwork',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255, verbose_name='name')),
                ('slug', models.SlugField(max_length=255, unique=True, verbose_name='slug')),
            ],
            options={
                'verbose_name_plural': 'affiliate networks',
                'ordering': ('name',),
                'verbose_name': 'affiliate network',
            },
        ),
        migrations.AddField(
            model_name='affiliateitem',
            name='network',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chiton_rack.AffiliateNetwork', verbose_name='affiliate network'),
        ),
    ]
