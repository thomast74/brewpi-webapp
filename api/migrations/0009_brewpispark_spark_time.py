# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_auto_20150405_1435'),
    ]

    operations = [
        migrations.AddField(
            model_name='brewpispark',
            name='spark_time',
            field=models.BigIntegerField(default=0, verbose_name=b'Spark Time'),
            preserve_default=True,
        ),
    ]
