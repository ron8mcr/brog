# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('filesharing', '0005_auto_20150215_1827'),
    ]

    operations = [
        migrations.AlterField(
            model_name='directory',
            name='allowed_users',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL, related_name='users_allowed'),
        ),
    ]
