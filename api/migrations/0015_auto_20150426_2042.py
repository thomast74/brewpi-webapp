# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_auto_20150425_1828'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='device',
            options={'ordering': ['spark', 'config_type'], 'get_latest_by': '-last_update', 'verbose_name': 'Device', 'verbose_name_plural': 'Devices'},
        ),
        migrations.RenameField(
            model_name='device',
            old_name='type',
            new_name='config_type',
        ),
        migrations.AlterField(
            model_name='brewpispark',
            name='device_mode',
            field=models.IntegerField(default=0, verbose_name=b'Device Mode', choices=[(0, b'MANUAL'), (1, b'CALIBRATION'), (2, b'LOGGING'), (3, b'AUTOMATIC')]),
        ),
        migrations.AlterField(
            model_name='configuration',
            name='type',
            field=models.IntegerField(verbose_name=b'Configuration Type', choices=[(0, b'None'), (1, b'Brew'), (2, b'Fermentation'), (3, b'Calibration')]),
        ),
    ]
