# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-16 10:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cfy_wrapper', '0002_container'),
    ]

    operations = [
        migrations.AddField(
            model_name='container',
            name='description',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
    ]
