# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-21 09:37
from __future__ import unicode_literals

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cfy_wrapper', '0004_auto_20160317_0910'),
    ]

    operations = [
        migrations.AddField(
            model_name='blueprint',
            name='outputs',
            field=jsonfield.fields.JSONField(blank=True, null=True),
        ),
    ]
