# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('filesharing', '0003_auto_20150220_1949'),
    ]

    operations = [
        migrations.AlterField(
            model_name='directory',
            name='access_type',
            field=models.IntegerField(choices=[(0, 'NONE'), (1, 'GROUP'), (2, 'REGISTERED'), (4, 'ALL')], verbose_name='Тип доступа', default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='directory',
            name='allowed_users',
            field=models.ManyToManyField(blank=True, related_name='users_allowed', verbose_name='Допущенные пользователи', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
