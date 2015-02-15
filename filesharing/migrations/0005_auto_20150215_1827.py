# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('filesharing', '0004_auto_20150215_1825'),
    ]

    operations = [
        migrations.AlterField(
            model_name='directory',
            name='allowed_users',
            field=models.ManyToManyField(blank=True, to='filesharing.UserProfile', related_name='users_allowed'),
        ),
    ]
