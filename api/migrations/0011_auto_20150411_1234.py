# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_device_function'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='brewpispark',
            name='board_revision',
        ),
        migrations.RemoveField(
            model_name='brewpispark',
            name='device_config',
        ),
    ]
