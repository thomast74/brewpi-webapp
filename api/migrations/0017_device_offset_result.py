# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0016_auto_20150430_2218'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='offset_result',
            field=models.CharField(default=b'', max_length=30, verbose_name=b'Calibration Result'),
        ),
    ]
