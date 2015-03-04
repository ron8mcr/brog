# -*- coding: utf-8 -*-
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.auth.models import AbstractUser
import os
from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from mptt.managers import TreeManager
from django.db.models.manager import Manager
from django.db.utils import IntegrityError
from django.db.models.signals import pre_save, pre_delete
from django.core.exceptions import ValidationError


class User(AbstractUser):

    @property
    def home_directory(self):
        return Directory.objects.root_nodes().get(owner=self)


# создание домашней папки для каждого пользователя
@receiver(user_signed_up)
def make_home_dir(user, **kwargs):
    Directory.objects.create(name=user.username, owner=user)


class AccessType(object):
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


class DirectoryManager(TreeManager):
    """ Собственный менеджер для директорий.
    Добавляет возможность выбора директории по полному пути
    """

    def get_by_full_path(self, path):
        # TODO: переделать всю
        dirs_in_path = [i for i in path.split('/') if i]
        if not dirs_in_path:
            return None

        parent = self.root_nodes().get(name=dirs_in_path[0])

        for d in dirs_in_path[1:]:
            parent = parent.get_children().get(name=d)

        return parent


class CheckNameMixin(object):
    """
    проверка имени файла/директории на лишние символы и уникальность
    """
    def clean(self):
        if '/' in self.name:
            raise ValidationError("Запрещено использовать такие символы в имени")

        if Directory.objects.filter(parent=self.parent, name=self.name).first():
            raise ValidationError(
                "В данной директории есть директория с тем же именем")

        if File.objects.filter(parent=self.parent, name=self.name).first():
            raise ValidationError(
                "В данной директории есть файл с тем же именем")


class Directory(CheckNameMixin, MPTTModel):
    objects = DirectoryManager()
    name = models.CharField(max_length=256,
                            verbose_name="Имя")
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
        return os.path.join('/', *[i.name for i in
                                   self.get_ancestors(include_self=True)])

    def has_access(self, user):
        if self.access_type == AccessType.ALL:
            return True
        elif self.access_type == AccessType.NONE:
            return user == self.owner
        elif self.access_type == AccessType.GROUP:
            return user in self.allowed_users.all()
        elif self.access_type == AccessType.REGISTERED:
            return user.is_authenticated()
        return None

    def clean(self):
        if not self.has_access(self.owner):
            raise ValidationError(
                "Вам сюда доступ запрещён")
        super(Directory, self).clean()

    class MPTTMeta(object):
        order_insertion_by = ['name']

    class Meta(object):
        verbose_name = "Директория"
        verbose_name_plural = "Директории"
        unique_together = ("parent", "name")


class FileManager(Manager):

    """ Собственный менеджер для файлов.
    Добавляет возможность поиска файла по полному пути
    """

    def get_by_full_path(self, path):
        path = path.rstrip('/')
        dirs_path, name = os.path.split(path)
        parent = Directory.objects.get_by_full_path(dirs_path)
        return self.get(name=name, parent=parent)


class File(CheckNameMixin, models.Model):
    objects = FileManager()
    my_file = models.FileField(verbose_name="Файл")
    parent = models.ForeignKey(Directory,
                               verbose_name="Родительская директория")
    name = models.CharField(max_length=256, verbose_name="Имя", blank=True)

    def __str__(self):
        return self.full_path

    @property
    def full_path(self):
        return os.path.join(self.parent.full_path, self.name)

    def has_access(self, user):
        return self.parent.has_access(user)

    def clean(self):
        if not self.name:
            self.name = os.path.basename(self.my_file.name)
        super(File, self).clean()

    class Meta(object):
        verbose_name = "Файл"
        verbose_name_plural = "Файлы"
        unique_together = ("parent", "name")


@receiver(pre_delete, sender=File)
def file_delete(instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.my_file.delete(False)


# исключаем сохранение в одной директории
# файлов и директорий с одинаковыми именами
@receiver(pre_save, sender=File)
@receiver(pre_save, sender=Directory)
def check_duplicate(sender, instance, **kwargs):
    if sender == Directory:
        another_type = File
    else:
        another_type = Directory
    parent = instance.parent
    try:
        # если файла|директории нет - всё нормально
        # если есть - ошибка
        another_type.objects.get(parent=parent, name=instance.name)
    except another_type.DoesNotExist:
        return
    raise IntegrityError("В одной директории не может быть "
                         "файла и директории с одинаковыми именами")