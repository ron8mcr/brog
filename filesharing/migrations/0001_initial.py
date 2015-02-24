# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.utils.timezone
import filesharing.models
import django.core.validators
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, verbose_name='superuser status', help_text='Designates that this user has all permissions without explicitly assigning them.')),
                ('username', models.CharField(help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', verbose_name='username', max_length=30, unique=True, validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username.', 'invalid')])),
                ('first_name', models.CharField(verbose_name='first name', blank=True, max_length=30)),
                ('last_name', models.CharField(verbose_name='last name', blank=True, max_length=30)),
                ('email', models.EmailField(verbose_name='email address', blank=True, max_length=75)),
                ('is_staff', models.BooleanField(default=False, verbose_name='staff status', help_text='Designates whether the user can log into this admin site.')),
                ('is_active', models.BooleanField(default=True, verbose_name='active', help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(related_name='user_set', to='auth.Group', verbose_name='groups', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of his/her group.', related_query_name='user')),
                ('user_permissions', models.ManyToManyField(related_name='user_set', to='auth.Permission', verbose_name='user permissions', blank=True, help_text='Specific permissions for this user.', related_query_name='user')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Directory',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('name', models.CharField(verbose_name='Имя', max_length=256, validators=[filesharing.models.name_valid])),
                ('access_type', models.IntegerField(choices=[(0, 'NONE'), (1, 'GROUP'), (2, 'REGISTERED'), (4, 'ALL')], default=0, verbose_name='Тип доступа')),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('allowed_users', models.ManyToManyField(related_name='users_allowed', verbose_name='Допущенные пользователи', blank=True, to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(related_name='user_owner', verbose_name='Владелец', to=settings.AUTH_USER_MODEL)),
                ('parent', mptt.fields.TreeForeignKey(related_name='children', null=True, verbose_name='Родительская директория', blank=True, to='filesharing.Directory')),
            ],
            options={
                'verbose_name': 'Директория',
                'verbose_name_plural': 'Директории',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('my_file', models.FileField(verbose_name='Файл', upload_to='')),
                ('name', models.CharField(verbose_name='Имя', blank=True, max_length=256)),
                ('parent', models.ForeignKey(to='filesharing.Directory', verbose_name='Родительская директория')),
            ],
            options={
                'verbose_name': 'Файл',
                'verbose_name_plural': 'Файлы',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='file',
            unique_together=set([('parent', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='directory',
            unique_together=set([('parent', 'name')]),
        ),
    ]
