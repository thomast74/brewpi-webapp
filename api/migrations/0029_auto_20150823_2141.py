# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0028_auto_20150609_2354'),
    ]

    operations = [
        migrations.AddField(
            model_name='configuration',
            name='cool_actuator_id',
            field=models.IntegerField(null=True, verbose_name=b'Cool Actuator'),
        ),
        migrations.AddField(
            model_name='configuration',
            name='fan_actuator_id',
            field=models.IntegerField(null=True, verbose_name=b'Fan Actuator'),
        ),
    ]
