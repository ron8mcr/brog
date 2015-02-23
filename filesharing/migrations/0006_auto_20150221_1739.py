# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('filesharing', '0005_auto_20150221_1721'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='directory',
            unique_together=set([('parent', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='file',
            unique_together=set([('parent', 'name')]),
        ),
    ]
