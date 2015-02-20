# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings
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
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', unique=True, max_length=30, verbose_name='username', validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username.', 'invalid')])),
                ('first_name', models.CharField(max_length=30, blank=True, verbose_name='first name')),
                ('last_name', models.CharField(max_length=30, blank=True, verbose_name='last name')),
                ('email', models.EmailField(max_length=75, blank=True, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('my_field', models.CharField(max_length=256)),
                ('groups', models.ManyToManyField(related_query_name='user', related_name='user_set', help_text='The groups this user belongs to. A user will get all permissions granted to each of his/her group.', blank=True, verbose_name='groups', to='auth.Group')),
                ('user_permissions', models.ManyToManyField(related_query_name='user', related_name='user_set', help_text='Specific permissions for this user.', blank=True, verbose_name='user permissions', to='auth.Permission')),
            ],
            options={
                'abstract': False,
                'verbose_name_plural': 'users',
                'verbose_name': 'user',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Directory',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('access_type', models.CharField(max_length=20)),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('allowed_users', models.ManyToManyField(blank=True, related_name='users_allowed', to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(related_name='user_owner', to=settings.AUTH_USER_MODEL)),
                ('parent', mptt.fields.TreeForeignKey(related_name='children', blank=True, null=True, to='filesharing.Directory')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('my_file', models.FileField(upload_to='')),
                ('parent', models.ForeignKey(to='filesharing.Directory')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
