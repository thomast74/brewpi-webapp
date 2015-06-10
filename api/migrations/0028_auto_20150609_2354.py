# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0027_auto_20150609_2351'),
    ]

    operations = [
        migrations.RenameField(
            model_name='configuration',
            old_name='heat_actuator',
            new_name='heat_actuator_id',
        ),
        migrations.RenameField(
            model_name='configuration',
            old_name='temp_sensor',
            new_name='temp_sensor_id',
        ),
    ]
