# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0023_auto_20150604_2346'),
    ]

    operations = [
        migrations.AddField(
            model_name='configuration',
            name='heat_actuator',
            field=models.IntegerField(null=True, verbose_name=b'Heat Actuator'),
        ),
    ]
