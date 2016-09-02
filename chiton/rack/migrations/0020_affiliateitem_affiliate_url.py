# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-30 20:48
from __future__ import unicode_literals

from django.db import migrations, models


def clone_urls(apps, schema_editor):
    """Use each affiliate item's URL as its affiliate URL."""
    AffiliateItem = apps.get_model('chiton_rack', 'AffiliateItem')

    for item in AffiliateItem.objects.all():
        item.affiliate_url = item.url
        item.save()


class Migration(migrations.Migration):

    dependencies = [
        ('chiton_rack', '0019_affiliateitem_retailer'),
    ]

    operations = [
        migrations.AddField(
            model_name='affiliateitem',
            name='affiliate_url',
            field=models.TextField(default='http://example.com', verbose_name='affiliate URL'),
            preserve_default=False,
        ),
        migrations.RunPython(clone_urls)
    ]