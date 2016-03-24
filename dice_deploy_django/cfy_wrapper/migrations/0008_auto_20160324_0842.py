# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-24 08:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cfy_wrapper', '0007_auto_20160323_1418'),
    ]

    operations = [
        migrations.AddField(
            model_name='blueprint',
            name='yaml',
            field=models.FileField(blank=True, null=True, upload_to=b'blueprints_yaml'),
        ),
        migrations.AlterField(
            model_name='blueprint',
            name='archive',
            field=models.FileField(blank=True, null=True, upload_to=b'blueprints_targz'),
        ),
    ]
