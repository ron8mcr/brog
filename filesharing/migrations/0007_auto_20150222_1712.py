# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import filesharing.models


class Migration(migrations.Migration):

    dependencies = [
        ('filesharing', '0006_auto_20150221_1739'),
    ]

    operations = [
        migrations.AlterField(
            model_name='directory',
            name='name',
            field=models.CharField(verbose_name='Имя', validators=[filesharing.models.name_valid], max_length=256),
            preserve_default=True,
        ),
    ]
