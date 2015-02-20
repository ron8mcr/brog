# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('filesharing', '0002_auto_20150220_1945'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='directory',
            options={'verbose_name': 'Директория', 'verbose_name_plural': 'Директории'},
        ),
        migrations.AddField(
            model_name='directory',
            name='access_type',
            field=models.IntegerField(choices=[(0, 'NONE'), (1, 'GROUP'), (2, 'REGISTERED'), (3, 'ALL')], default=0),
            preserve_default=True,
        ),
    ]
