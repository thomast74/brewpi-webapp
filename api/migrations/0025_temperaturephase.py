# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0024_configuration_heat_actuator'),
    ]

    operations = [
        migrations.CreateModel(
            name='TemperaturePhase',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField(verbose_name=b'Order')),
                ('start_date', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0), verbose_name=b'Start Date')),
                ('duration', models.IntegerField(default=0, verbose_name=b'Duration')),
                ('temperature', models.FloatField(verbose_name=b'Temperature')),
                ('done', models.BooleanField(default=False, verbose_name=b'Done')),
                ('configuration', models.ForeignKey(verbose_name=b'Configuration', to='api.Configuration')),
            ],
            options={
                'ordering': ['configuration', 'order'],
                'verbose_name': 'Temperature Phase',
                'verbose_name_plural': 'Temperature Phases',
            },
        ),
    ]
