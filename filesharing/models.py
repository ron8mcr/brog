# -*- coding: utf-8 -*-
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.auth.models import AbstractUser
import os
from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from django.db.models.signals import pre_save


class User(AbstractUser):
    @property
    def home_directory(self):
        return Directory.objects.root_nodes().filter(owner=self.user)


@receiver(user_signed_up)
def make_home_dir(user, **kwargs):
    home_dir = Directory.objects.create(name=user.username, owner=user)


class AccessType():
    NONE = 0
    GROUP = 1
    REGISTERED = 2
    ALL = 4

    GROUP_CHOICES = (
        (NONE, 'NONE'),
        (GROUP, 'GROUP'),
        (REGISTERED, 'REGISTERED'),
        (ALL, 'ALL')
    )


class Directory(MPTTModel):
    name = models.CharField(max_length=256, verbose_name="Название")
    owner = models.ForeignKey(User, related_name="user_owner",
                              verbose_name="Владелец")
    parent = TreeForeignKey('self', null=True, blank=True,
                            related_name='children',
                            verbose_name="Родительская директория")
    access_type = models.IntegerField(choices=AccessType.GROUP_CHOICES,
                                      default=AccessType.NONE,
                                      verbose_name="Тип доступа")

    # пользователи, которым разрешён доступ (если таковые имеются)
    allowed_users = models.ManyToManyField(
        User, blank=True, related_name="users_allowed",
        verbose_name="Допущенные пользователи")

    def __str__(self):
        return self.full_path

    @property
    def full_path(self):
        return os.path.join(*[i.name for i in self.get_ancestors(include_self=True)])

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = "Директория"
        verbose_name_plural = "Директории"


class File(models.Model):
    my_file = models.FileField(verbose_name="Файл")
    parent = models.ForeignKey(Directory,
                               verbose_name="Родительская директория")

    def __str__(self):
        return self.full_path

    @property
    def file_name(self):
        return os.path.basename(self.my_file.name)

    @property
    def full_path(self):
        return os.path.join(self.parent.full_path, self.file_name)

    class Meta():
        verbose_name = "Файл"
        verbose_name_plural = "Файлы"
