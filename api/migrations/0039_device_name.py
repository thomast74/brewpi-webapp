# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-05-21 21:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0038_configuration_archived'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='name',
            field=models.CharField(max_length=30, null=True, verbose_name=b'Name'),
        ),
    ]