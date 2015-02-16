# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('filesharing', '0006_auto_20150216_1633'),
    ]

    operations = [
        migrations.AlterField(
            model_name='directory',
            name='allowed_users',
            field=models.ManyToManyField(to='filesharing.UserProfile', blank=True, related_name='users_allowed'),
        ),
        migrations.AlterField(
            model_name='directory',
            name='owner',
            field=models.ForeignKey(to='filesharing.UserProfile', related_name='user_owner'),
        ),
    ]
