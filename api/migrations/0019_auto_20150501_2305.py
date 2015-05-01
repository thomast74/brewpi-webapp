# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0018_device_offset_from_spark'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='device',
            options={'ordering': ['spark', 'device_type'], 'get_latest_by': '-last_update', 'verbose_name': 'Device', 'verbose_name_plural': 'Devices'},
        ),
        migrations.RenameField(
            model_name='device',
            old_name='config_type',
            new_name='device_type',
        ),
    ]
