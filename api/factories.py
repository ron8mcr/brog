from filesharing.models import User, AccessType, Directory, File
import factory
import random
from tempfile import TemporaryFile

class UserFactory(factory.django.DjangoModelFactory):
     class Meta:
        model = User
    
    password = '123456'

    
class DirFactory(factory.django.DjangoModelFactory):
      class Meta:
        model = Directory


class FileFactory(factory.django.DjangoModelFactory):
      class Meta:
        model = File
        
      my_file = TemporaryFile()
