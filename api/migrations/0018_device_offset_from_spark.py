# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0017_device_offset_result'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='offset_from_spark',
            field=models.FloatField(default=0, verbose_name=b'Offset From Spark'),
        ),
    ]
