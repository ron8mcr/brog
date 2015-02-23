# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import filesharing.models


class Migration(migrations.Migration):

    dependencies = [
        ('filesharing', '0005_auto_20150221_2335'),
    ]

    operations = [
        migrations.AlterField(
            model_name='directory',
            name='name',
            field=models.CharField(max_length=256, verbose_name=b'\xd0\x98\xd0\xbc\xd1\x8f', validators=[filesharing.models.name_valid]),
            preserve_default=True,
        ),
    ]
