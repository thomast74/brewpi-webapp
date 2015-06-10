# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0026_auto_20150609_2337'),
    ]

    operations = [
        migrations.AlterField(
            model_name='configuration',
            name='spark',
            field=models.ForeignKey(verbose_name=b'Spark', to='api.BrewPiSpark'),
        ),
    ]
