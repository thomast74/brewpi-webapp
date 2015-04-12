# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('api', '0009_brewpispark_spark_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='function',
            field=models.IntegerField(default=0, verbose_name=b'Device Function',
                                      choices=[(0, b'None'), (1, b'Fridge Cooling Actuator'),
                                               (2, b'Fridge Heating Actuator'), (3, b'Fridge Fan Actuator'),
                                               (4, b'HLT Heating Actuator'), (5, b'Boil Heating Actuator'),
                                               (6, b'Pump 1 Actuator'), (7, b'Pump 2 Actuator'),
                                               (8, b'Fridge Beer Temp Sensor'), (9, b'Fridge Inside Temp Sensor'),
                                               (10, b'Outside Fridge Temp Sensor'), (11, b'HLT In Temp Sensor'),
                                               (12, b'HLT Out Temp Sensor'), (13, b'Mash In Temp Sensor'),
                                               (14, b'Mash Out Temp Sensor'), (15, b'Boil In Temp Sensor'),
                                               (16, b'Boil Inside Temp Sensor'), (17, b'Boil Out Temp Sensor')]),
            preserve_default=True,
        ),
    ]
