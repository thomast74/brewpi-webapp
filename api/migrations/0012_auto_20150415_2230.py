# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_auto_20150411_1234'),
    ]

    operations = [
        migrations.CreateModel(
            name='Configuration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=30, verbose_name=b'Name')),
                ('create_date', models.DateTimeField(verbose_name=b'Create Date', editable=False)),
                ('type', models.IntegerField(verbose_name=b'Configuration Type', choices=[(0, b'None'), (1, b'Brew'), (2, b'Fermentation')])),
                ('spark', models.ForeignKey(to='api.BrewPiSpark', null=True)),
            ],
            options={
                'ordering': ['create_date', 'name'],
                'get_latest_by': '-create_date',
                'verbose_name': 'Configuration',
                'verbose_name_plural': 'Configurations',
            },
        ),
        migrations.AlterField(
            model_name='device',
            name='function',
            field=models.IntegerField(default=0, verbose_name=b'Device Function', choices=[(0, b'None'), (1, b'Fridge Cooling Actuator'), (2, b'Fridge Heating Actuator'), (3, b'Fridge Fan Actuator'), (4, b'HLT Heating Actuator'), (5, b'Boil Heating Actuator'), (6, b'Pump 1 Actuator'), (7, b'Pump 2 Actuator'), (8, b'Fridge Beer 1 Temp Sensor'), (9, b'Fridge Beer 2 Temp Sensor'), (10, b'Fridge Beer 3 Temp Sensor'), (11, b'Fridge Inside Temp Sensor'), (12, b'Outside Fridge Temp Sensor'), (13, b'HLT In Temp Sensor'), (14, b'HLT Out Temp Sensor'), (15, b'Mash In Temp Sensor'), (16, b'Mash Out Temp Sensor'), (17, b'Boil In Temp Sensor'), (18, b'Boil Inside Temp Sensor'), (19, b'Boil Out Temp Sensor')]),
        ),
        migrations.AddField(
            model_name='device',
            name='configuration',
            field=models.ForeignKey(to='api.Configuration', null=True),
        ),
    ]
