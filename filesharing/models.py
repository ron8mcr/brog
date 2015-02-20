# -*- coding: utf-8 -*-
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.auth.models import AbstractUser
import os


class User(AbstractUser):
    my_field = models.CharField(max_length=256)

    def get_home_directory(self):
        return Directory.objects.root_nodes().filter(owner=self.user)


class Directory(MPTTModel):
    name = models.CharField(max_length=256)
    owner = models.ForeignKey(User, related_name="user_owner")

    # пользователи, которым разрешён доступ (если таковые имеются)
    allowed_users = models.ManyToManyField(
        User, blank=True, related_name="users_allowed")

    # какой группе разрешен доступ
    # 'all' - всем
    # 'all_registered' - всем зарегестрированным
    # 'group' - группе зарегистрированных пользователей
    # 'none' - только владельцу
    access_type = models.CharField(max_length=20)
    parent = TreeForeignKey('self', null=True, blank=True,
                            related_name='children')

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.get_full_path()
        #return self.name

    def get_full_path(self):
        return '/'.join([i.name for i in self.get_ancestors(include_self=True)])


class File(models.Model):
    #parent = TreeForeignKey(Directory,
                        # null=True, blank=True, related_name='children')
    my_file = models.FileField()
    parent = models.ForeignKey(Directory)

    def __str__(self):
         return self.get_full_path()

    def get_full_path(self):
        return self.parent.get_full_path() + '/' + self.get_file_name()

    def get_file_name(self):
        return os.path.basename(self.my_file.name)