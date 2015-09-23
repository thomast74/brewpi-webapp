# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0029_auto_20150823_2141'),
    ]

    operations = [
        migrations.CreateModel(
            name='BrewPi',
            fields=[
                ('device_id', models.CharField(max_length=30, serialize=False, verbose_name=b'Device Id', primary_key=True)),
                ('name', models.CharField(max_length=30, unique=True, null=True, verbose_name=b'Name')),
                ('firmware_version', models.FloatField(default=0.0, verbose_name=b'Firmware Version')),
                ('ip_address', models.GenericIPAddressField(verbose_name=b'Ip Address')),
                ('web_address', models.GenericIPAddressField(null=True, verbose_name=b'Web Address')),
                ('web_port', models.IntegerField(null=True, verbose_name=b'Web Port')),
                ('brewpi_time', models.BigIntegerField(default=0, verbose_name=b'BrewPi Time')),
                ('last_update', models.DateTimeField(verbose_name=b'Last Update')),
            ],
            options={
                'ordering': ['name', 'device_id'],
                'get_latest_by': '-last_update',
                'verbose_name': 'BrewPi',
                'verbose_name_plural': 'BrewPis',
            },
        ),
        migrations.CreateModel(
            name='Phase',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateTimeField(verbose_name=b'Start Date')),
                ('temperature', models.FloatField(verbose_name=b'Temperature')),
                ('heat_pwm', models.FloatField(verbose_name=b'Heat PWM')),
                ('fan_pwm', models.FloatField(verbose_name=b'Fan PWM')),
                ('p', models.FloatField(verbose_name=b'P')),
                ('i', models.FloatField(verbose_name=b'I')),
                ('d', models.FloatField(verbose_name=b'D')),
                ('done', models.BooleanField(default=False, verbose_name=b'Done')),
            ],
            options={
                'ordering': ['configuration', 'start_date'],
                'verbose_name': 'Phase',
                'verbose_name_plural': 'Phases',
            },
        ),
        migrations.RemoveField(
            model_name='temperaturephase',
            name='configuration',
        ),
        migrations.RemoveField(
            model_name='configuration',
            name='spark',
        ),
        migrations.AddField(
            model_name='device',
            name='offset_from_brewpi',
            field=models.FloatField(default=0, verbose_name=b'Offset From BrewPi'),
        ),
        migrations.DeleteModel(
            name='TemperaturePhase',
        ),
        migrations.AddField(
            model_name='phase',
            name='configuration',
            field=models.ForeignKey(related_name='phases', verbose_name=b'Configuration', to='api.Configuration'),
        ),
        migrations.RemoveField(
            model_name='device',
            name='is_invert',
        ),
        migrations.RemoveField(
            model_name='device',
            name='offset_from_spark',
        ),
        migrations.AddField(
            model_name='configuration',
            name='brewpi',
            field=models.ForeignKey(verbose_name=b'BrewPi', to='api.BrewPi', null=True),
        ),
        migrations.AddField(
            model_name='device',
            name='brewpi',
            field=models.ForeignKey(to='api.BrewPi', null=True),
        ),
        migrations.AlterModelOptions(
            name='device',
            options={'ordering': ['brewpi', 'device_type'], 'get_latest_by': '-last_update', 'verbose_name': 'Device', 'verbose_name_plural': 'Devices'},
        ),
        migrations.AlterUniqueTogether(
            name='device',
            unique_together=set([('pin_nr', 'hw_address', 'brewpi')]),
        ),
        migrations.DeleteModel(
            name='BrewPiSpark',
        ),
        migrations.RemoveField(
            model_name='device',
            name='spark',
        ),
    ]
