# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20150329_2307'),
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.IntegerField(default=0, verbose_name=b'Hardware Type', choices=[(0, b'None'), (1, b'Pin'), (2, b'OneWire Temp')])),
                ('pin_nr', models.IntegerField(default=0, verbose_name=b'Pin Nr')),
                ('hw_address', models.CharField(max_length=16, verbose_name=b'Hardware Address')),
                ('is_invert', models.BooleanField(default=True, verbose_name=b'Is Invert?')),
                ('is_deactivate', models.BooleanField(default=False, verbose_name=b'Is Deactivate?')),
                ('last_update', models.DateTimeField(verbose_name=b'Last Update')),
                ('spark', models.ForeignKey(to='api.BrewPiSpark')),
            ],
            options={
                'ordering': ['spark', 'type'],
                'get_latest_by': '-last_update',
                'verbose_name': 'Device',
                'verbose_name_plural': 'Devices',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='device',
            unique_together=set([('pin_nr', 'hw_address')]),
        ),
    ]
