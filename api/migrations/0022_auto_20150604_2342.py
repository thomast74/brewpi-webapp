# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0021_auto_20150603_2339'),
    ]

    operations = [
        migrations.AddField(
            model_name='configuration',
            name='temp_sensor_function',
            field=models.IntegerField(default=0, verbose_name=b'Temp Sensor'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='configuration',
            name='spark',
            field=models.ForeignKey(default=0, to='api.BrewPiSpark'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='device',
            name='function',
            field=models.IntegerField(default=0, verbose_name=b'Device Function', choices=[(0, b'None'), (1, b'Fridge Cooling Actuator'), (2, b'Fridge Heating Actuator'), (3, b'Fridge Fan Actuator'), (4, b'HLT Heating Actuator'), (5, b'Boil Heating Actuator'), (6, b'Pump 1 Actuator'), (7, b'Pump 2 Actuator'), (8, b'Fridge Beer 1 Temp Sensor'), (9, b'Fridge Beer 2 Temp Sensor'), (10, b'Fridge Beer 3 Temp Sensor'), (11, b'Fridge Inside Temp Sensor'), (12, b'Outside Fridge Temp Sensor'), (13, b'HLT In Temp Sensor'), (14, b'HLT Inside Temp Sensor'), (15, b'HLT Out Temp Sensor'), (16, b'Mash In Temp Sensor'), (17, b'Mash Inside Temp Sensor'), (18, b'Mash Out Temp Sensor'), (19, b'Boil In Temp Sensor'), (20, b'Boil Inside Temp Sensor'), (21, b'Boil Out Temp Sensor')]),
        ),
    ]
