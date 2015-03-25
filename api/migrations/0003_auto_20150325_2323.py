# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20150321_2304'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brewpispark',
            name='device_config',
            field=models.FloatField(default=0.0, verbose_name=b'Device Config'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='brewpispark',
            name='device_mode',
            field=models.CharField(default=b'MANUAL', max_length=20, verbose_name=b'Device Mode'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='brewpispark',
            name='firmware_version',
            field=models.FloatField(default=0.0, verbose_name=b'Firmware Version'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='brewpispark',
            name='name',
            field=models.CharField(max_length=100, unique=True, null=True, verbose_name=b'Name'),
            preserve_default=True,
        ),
    ]
