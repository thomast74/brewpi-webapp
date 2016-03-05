# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0031_auto_20150924_0011'),
    ]

    operations = [
        migrations.AddField(
            model_name='phase',
            name='cooling_off_period',
            field=models.IntegerField(default=180000, verbose_name=b'Cooling Off Period'),
        ),
        migrations.AddField(
            model_name='phase',
            name='cooling_on_period',
            field=models.IntegerField(default=600000, verbose_name=b'Cooling On Period'),
        ),
        migrations.AddField(
            model_name='phase',
            name='heating_period',
            field=models.IntegerField(default=4000, verbose_name=b'Heating Period'),
        ),
        migrations.AlterField(
            model_name='phase',
            name='d',
            field=models.FloatField(default=0, verbose_name=b'D'),
        ),
        migrations.AlterField(
            model_name='phase',
            name='fan_pwm',
            field=models.FloatField(default=200, verbose_name=b'Fan PWM'),
        ),
        migrations.AlterField(
            model_name='phase',
            name='heat_pwm',
            field=models.FloatField(default=0, verbose_name=b'Heat PWM'),
        ),
        migrations.AlterField(
            model_name='phase',
            name='i',
            field=models.FloatField(default=0, verbose_name=b'I'),
        ),
        migrations.AlterField(
            model_name='phase',
            name='p',
            field=models.FloatField(default=0, verbose_name=b'P'),
        ),
        migrations.AlterField(
            model_name='phase',
            name='temperature',
            field=models.FloatField(default=0, verbose_name=b'Temperature'),
        ),
    ]
