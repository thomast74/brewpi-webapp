# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0020_auto_20150502_1121'),
    ]

    operations = [
        migrations.AlterField(
            model_name='configuration',
            name='name',
            field=models.CharField(max_length=30, verbose_name=b'Name'),
        ),
    ]
