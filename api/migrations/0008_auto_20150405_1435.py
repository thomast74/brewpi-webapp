# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_auto_20150405_1121'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='value',
            field=models.CharField(default=b'', max_length=10, verbose_name=b'Value'),
            preserve_default=True,
        ),
    ]
