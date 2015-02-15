# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('filesharing', '0003_auto_20150215_1822'),
    ]

    operations = [
        migrations.AlterField(
            model_name='directory',
            name='owner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='user_owner'),
        ),
    ]
