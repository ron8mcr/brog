# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('filesharing', '0004_auto_20150220_2043'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='name',
            field=models.CharField(blank=True, verbose_name='Имя', max_length=256),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='directory',
            name='name',
            field=models.CharField(verbose_name='Имя', max_length=256),
            preserve_default=True,
        ),
    ]
