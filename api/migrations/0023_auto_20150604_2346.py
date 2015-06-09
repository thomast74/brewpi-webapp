# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0022_auto_20150604_2342'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='configuration',
            name='temp_sensor_function',
        ),
        migrations.AddField(
            model_name='configuration',
            name='temp_sensor',
            field=models.IntegerField(null=True, verbose_name=b'Temp Sensor'),
        ),
    ]
