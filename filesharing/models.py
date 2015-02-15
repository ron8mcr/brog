from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile')


class Directory(MPTTModel):
    name = models.CharField(max_length=256)
    owner = models.ForeignKey(User, related_name="user_owner")

    # пользователи, которым разрешён доступ (если таковые имеются)
    allowed_users = models.ManyToManyField(UserProfile, blank=True, related_name="users_allowed")

    # какой группе разрешен доступ
    # 'all' - всем
    # 'all_registered' - всем зарегестрированным
    # 'group' - группе зарегистрированных пользователей
    # 'none' - только владельцу
    access_type = models.CharField(max_length=20)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')
    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return '/'.join([i.name for i in self.get_ancestors(include_self=True)])
        #return self.name

class File(models.Model):
    #parent = TreeForeignKey(Directory, null=True, blank=True, related_name='children')
    my_file = models.FileField()
    parent = models.ForeignKey(Directory)

