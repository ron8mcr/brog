# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('filesharing', '0004_auto_20150220_2043'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='name',
            field=models.CharField(default=1, max_length=256, verbose_name=b'\xd0\x98\xd0\xbc\xd1\x8f', blank=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='directory',
            name='access_type',
            field=models.IntegerField(default=0, verbose_name=b'\xd0\xa2\xd0\xb8\xd0\xbf \xd0\xb4\xd0\xbe\xd1\x81\xd1\x82\xd1\x83\xd0\xbf\xd0\xb0', choices=[(0, b'NONE'), (1, b'GROUP'), (2, b'REGISTERED'), (4, b'ALL')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='directory',
            name='allowed_users',
            field=models.ManyToManyField(related_name='users_allowed', verbose_name=b'\xd0\x94\xd0\xbe\xd0\xbf\xd1\x83\xd1\x89\xd0\xb5\xd0\xbd\xd0\xbd\xd1\x8b\xd0\xb5 \xd0\xbf\xd0\xbe\xd0\xbb\xd1\x8c\xd0\xb7\xd0\xbe\xd0\xb2\xd0\xb0\xd1\x82\xd0\xb5\xd0\xbb\xd0\xb8', to=settings.AUTH_USER_MODEL, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='directory',
            name='name',
            field=models.CharField(max_length=256, verbose_name=b'\xd0\x98\xd0\xbc\xd1\x8f'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='directory',
            name='owner',
            field=models.ForeignKey(related_name='user_owner', verbose_name=b'\xd0\x92\xd0\xbb\xd0\xb0\xd0\xb4\xd0\xb5\xd0\xbb\xd0\xb5\xd1\x86', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='directory',
            name='parent',
            field=mptt.fields.TreeForeignKey(related_name='children', verbose_name=b'\xd0\xa0\xd0\xbe\xd0\xb4\xd0\xb8\xd1\x82\xd0\xb5\xd0\xbb\xd1\x8c\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f \xd0\xb4\xd0\xb8\xd1\x80\xd0\xb5\xd0\xba\xd1\x82\xd0\xbe\xd1\x80\xd0\xb8\xd1\x8f', blank=True, to='filesharing.Directory', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='file',
            name='my_file',
            field=models.FileField(upload_to=b'', verbose_name=b'\xd0\xa4\xd0\xb0\xd0\xb9\xd0\xbb'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='file',
            name='parent',
            field=models.ForeignKey(verbose_name=b'\xd0\xa0\xd0\xbe\xd0\xb4\xd0\xb8\xd1\x82\xd0\xb5\xd0\xbb\xd1\x8c\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f \xd0\xb4\xd0\xb8\xd1\x80\xd0\xb5\xd0\xba\xd1\x82\xd0\xbe\xd1\x80\xd0\xb8\xd1\x8f', to='filesharing.Directory'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='directory',
            unique_together=set([('parent', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='file',
            unique_together=set([('parent', 'name')]),
        ),
    ]
