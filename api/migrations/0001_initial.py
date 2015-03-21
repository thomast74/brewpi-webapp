# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BrewPiSpark',
            fields=[
                ('device_id', models.CharField(max_length=30, serialize=False, verbose_name=b'Device Id', primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name=b'Name')),
                ('device_mode', models.CharField(max_length=20, verbose_name=b'Device Mode')),
                ('device_config', models.CharField(max_length=100, null=True, verbose_name=b'Device Config')),
                ('firmware_version', models.FloatField(verbose_name=b'Firmware Version')),
                ('board_revision', models.CharField(max_length=10, verbose_name=b'Board Revision')),
                ('ip_address', models.GenericIPAddressField(verbose_name=b'Ip Address')),
                ('last_update', models.DateTimeField(verbose_name=b'Last Update')),
            ],
            options={
                'ordering': ['name', 'device_id'],
                'get_latest_by': '-last_update',
                'verbose_name': 'BrewPi Spark',
                'verbose_name_plural': 'BrewPi Sparks',
            },
            bases=(models.Model,),
        ),
    ]
