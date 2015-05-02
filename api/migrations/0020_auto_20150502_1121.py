# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0019_auto_20150501_2305'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brewpispark',
            name='device_mode',
            field=models.CharField(default=b'M', max_length=1, verbose_name=b'Device Mode', choices=[(b'M', b'MANUAL'), (b'C', b'CALIBRATION'), (b'L', b'LOGGING'), (b'A', b'AUTOMATIC')]),
        ),
        migrations.AlterField(
            model_name='device',
            name='device_type',
            field=models.IntegerField(default=0, verbose_name=b'Hardware Type', choices=[(0, b'None'), (1, b'Actuator Digital'), (2, b'Actuator PWM'), (3, b'OneWire Temp. Sensor')]),
        ),
    ]
