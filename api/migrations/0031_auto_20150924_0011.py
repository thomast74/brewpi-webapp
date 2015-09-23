# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0030_auto_20150923_2344'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='value',
            field=models.FloatField(default=0, verbose_name=b'Value'),
        ),
    ]
