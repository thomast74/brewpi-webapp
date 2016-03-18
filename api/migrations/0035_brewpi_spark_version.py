# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0034_auto_20160317_2148'),
    ]

    operations = [
        migrations.AddField(
            model_name='brewpi',
            name='spark_version',
            field=models.CharField(default=b'', max_length=2, verbose_name=b'Spark Version'),
        ),
    ]
