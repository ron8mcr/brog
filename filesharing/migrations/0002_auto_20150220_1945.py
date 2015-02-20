# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('filesharing', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='file',
            options={'verbose_name': 'Файл', 'verbose_name_plural': 'Файлы'},
        ),
        migrations.RemoveField(
            model_name='directory',
            name='access_type',
        ),
        migrations.RemoveField(
            model_name='user',
            name='my_field',
        ),
        migrations.AlterField(
            model_name='directory',
            name='name',
            field=models.CharField(verbose_name='Название', max_length=256),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='directory',
            name='owner',
            field=models.ForeignKey(verbose_name='Владелец', to=settings.AUTH_USER_MODEL, related_name='user_owner'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='directory',
            name='parent',
            field=mptt.fields.TreeForeignKey(verbose_name='Родительская директория', to='filesharing.Directory', null=True, blank=True, related_name='children'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='file',
            name='my_file',
            field=models.FileField(verbose_name='Файл', upload_to=''),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='file',
            name='parent',
            field=models.ForeignKey(verbose_name='Родительская директория', to='filesharing.Directory'),
            preserve_default=True,
        ),
    ]
