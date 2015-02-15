# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('filesharing', '0002_auto_20150215_1818'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL, related_name='profile')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RenameModel(
            old_name='MyFile',
            new_name='File',
        ),
        migrations.AlterField(
            model_name='directory',
            name='allowed_users',
            field=models.ManyToManyField(related_name='users_allowed', to='filesharing.UserProfile'),
        ),
        migrations.AlterField(
            model_name='directory',
            name='owner',
            field=models.ForeignKey(related_name='user_owner', to='filesharing.UserProfile'),
        ),
        migrations.DeleteModel(
            name='User',
        ),
    ]
