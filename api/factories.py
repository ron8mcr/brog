from filesharing.models import User, Directory, File
import factory


class UserFactory(factory.django.DjangoModelFactory):
    class Meta(object):
        model = User

    username = factory.Sequence(lambda n: 'user_{}'.format(n))
    password = '123456'


class DirFactory(factory.django.DjangoModelFactory):
    class Meta(object):
        model = Directory

    name = factory.Sequence(lambda n: 'dir_{}'.format(n))
    owner = factory.LazyAttribute(lambda a: UserFactory())


class FileFactory(factory.django.DjangoModelFactory):
    class Meta(object):
        model = File

    name = factory.Sequence(lambda n: 'file_{}'.format(n))
    parent = factory.LazyAttribute(lambda a: DirFactory())
    my_file = factory.django.FileField(data=b'file content')
