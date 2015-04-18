# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_auto_20150415_2230'),
    ]

    operations = [
        migrations.AddField(
            model_name='brewpispark',
            name='web_port',
            field=models.IntegerField(null=True, verbose_name=b'Web Port'),
        ),
    ]
