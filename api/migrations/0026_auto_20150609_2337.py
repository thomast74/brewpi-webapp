# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0025_temperaturephase'),
    ]

    operations = [
        migrations.AlterField(
            model_name='temperaturephase',
            name='configuration',
            field=models.ForeignKey(related_name='phases', verbose_name=b'Configuration', to='api.Configuration'),
        ),
    ]
