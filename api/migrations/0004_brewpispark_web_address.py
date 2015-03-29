# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20150325_2323'),
    ]

    operations = [
        migrations.AddField(
            model_name='brewpispark',
            name='web_address',
            field=models.GenericIPAddressField(null=True, verbose_name=b'Web Address'),
            preserve_default=True,
        ),
    ]
