# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_brewpispark_web_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brewpispark',
            name='device_config',
            field=models.CharField(default=b'', max_length=8, verbose_name=b'Device Config'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='brewpispark',
            name='name',
            field=models.CharField(max_length=30, unique=True, null=True, verbose_name=b'Name'),
            preserve_default=True,
        ),
    ]
