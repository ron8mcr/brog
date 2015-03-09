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
from django.db.models.signals import pre_save, post_save, pre_delete
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from rest_framework.authtoken.models import Token


class User(AbstractUser):

    @property
    def home_directory(self):
        return Directory.objects.root_nodes().get(owner=self)


# создание домашней папки для каждого пользователя
@receiver(user_signed_up)
def make_home_dir(user, **kwargs):
    Directory.objects.create(name=user.username, owner=user)


@receiver(user_signed_up)
def make_token(user, **kwargs):
    Token.objects.create(user=user)


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


class FullPathMixin(object):
    """ Собственный менеджер для файлов/директорий.
    Добавляет возможность выбора директории по полному пути
    Путь передается по-разному из разных мест:
     /path, /path/, path/
    Поэтому так
    """
    def get(self, **kwargs):
        if 'full_path' in kwargs:
            path = kwargs['full_path']
            path = path.rstrip('/')
            path = os.path.join('/', path)
            kwargs['full_path'] = path
        return super(FullPathMixin, self).get(**kwargs)


class DirectoryManager(FullPathMixin, TreeManager):
    pass


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
    full_path = models.CharField(max_length=2048, verbose_name="Полный путь",
                                 blank=True)

    # пользователи, которым разрешён доступ (если таковые имеются)
    allowed_users = models.ManyToManyField(
        User, blank=True, related_name="users_allowed",
        verbose_name="Допущенные пользователи")

    def __str__(self):
        return self.full_path

    def has_access(self, user):
        if self.access_type == AccessType.ALL:
            return True
        elif self.access_type == AccessType.NONE:
            return user == self.owner
        elif self.access_type == AccessType.GROUP:
            return user in self.allowed_users.all() or user == self.owner
        elif self.access_type == AccessType.REGISTERED:
            return user.is_authenticated()
        return None

    class MPTTMeta(object):
        order_insertion_by = ['name']

    class Meta(object):
        verbose_name = "Директория"
        verbose_name_plural = "Директории"
        unique_together = ("parent", "name")


@receiver(pre_save, sender=Directory)
def set_dir_path(sender, instance, **kwargs):
    if instance.is_root_node():
        instance.full_path = os.path.join('/', instance.name)
    else:
        instance.full_path = os.path.join(instance.parent.full_path, instance.name)


@receiver(post_save, sender=Directory)
def update_children_path(sender, instance, **kwargs):
    """
    Обновление полных путей для всех вложенных папок и файлов
    """
    for file in File.objects.filter(parent=instance):
        file.full_path = os.path.join(instance.full_path, file.name)
        file.save()

    for child_dir in instance.get_children():
        child_dir.full_path = os.path.join(
            '/', *[i.name for i in child_dir.get_ancestors(include_self=True)])
        for file in File.objects.filter(parent=child_dir):
            file.full_path = os.path.join(child_dir.full_path, file.name)
            file.save()
        child_dir.save()


class FileManager(FullPathMixin,Manager):
    pass


class File(CheckNameMixin, models.Model):
    objects = FileManager()
    my_file = models.FileField(storage=FileSystemStorage(
        location=settings.SENDFILE_ROOT), verbose_name="Файл")
    parent = models.ForeignKey(Directory,
                               verbose_name="Родительская директория")
    name = models.CharField(max_length=256, verbose_name="Имя", blank=True)
    full_path = models.CharField(max_length=2048, verbose_name="Полный путь",
                                 blank=True)

    def __str__(self):
        return self.full_path

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


@receiver(pre_save, sender=File)
def set_file_name_path(instance, **kwargs):
    if not instance.name:
        instance.name = os.path.basename(instance.my_file.name)
    instance.full_path = os.path.join(instance.parent.full_path, instance.name)


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