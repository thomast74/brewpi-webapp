# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_auto_20150426_2042'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='offset',
            field=models.FloatField(default=0, verbose_name=b'Offset'),
        ),
    ]
