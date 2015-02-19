# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('filesharing', '0008_auto_20150218_1338'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, parent_link=True, to=settings.AUTH_USER_MODEL, serialize=False, primary_key=True)),
                ('my_field', models.CharField(max_length=128)),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            bases=('auth.user',),
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='user',
        ),
        migrations.AlterField(
            model_name='directory',
            name='allowed_users',
            field=models.ManyToManyField(to='filesharing.CustomUser', blank=True, related_name='users_allowed'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='directory',
            name='owner',
            field=models.ForeignKey(to='filesharing.CustomUser', related_name='user_owner'),
            preserve_default=True,
        ),
        migrations.DeleteModel(
            name='UserProfile',
        ),
    ]
