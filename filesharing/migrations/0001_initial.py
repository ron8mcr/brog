# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Directory',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=256)),
                ('access_type', models.CharField(max_length=20)),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('my_file', models.FileField(upload_to='')),
                ('parent', models.ForeignKey(to='filesharing.Directory')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='directory',
            name='allowed_users',
            field=models.ManyToManyField(related_name='users_allowed', to='filesharing.User'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='directory',
            name='owner',
            field=models.ForeignKey(related_name='user_owner', to='filesharing.User'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='directory',
            name='parent',
            field=mptt.fields.TreeForeignKey(related_name='children', to='filesharing.Directory', null=True, blank=True),
            preserve_default=True,
        ),
    ]
