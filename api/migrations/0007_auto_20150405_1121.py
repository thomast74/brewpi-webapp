# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_auto_20150404_1724'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='offset',
            field=models.BigIntegerField(default=0, verbose_name=b'Offset'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='device',
            name='value',
            field=models.BigIntegerField(default=0, verbose_name=b'Value'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='device',
            name='spark',
            field=models.ForeignKey(to='api.BrewPiSpark', null=True),
            preserve_default=True,
        ),
    ]
