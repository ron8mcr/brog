from rest_framework.test import APITestCase, APIRequestFactory, APIClient
from django.core.files import File as DjangoFile
from filesharing.models import User, AccessType, Directory, File
from rest_framework import status


class FileSharingApiTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create(username='user1', password='123456')
        self.user2 = User.objects.create(username='user2', password='123456')
        Directory.objects.create(name='user1', owner=self.user1)
        Directory.objects.create(name='user2', owner=self.user2)

        # /user1/dir1
        Directory.objects.create(name='dir1',
                                 parent=self.user1.home_directory,
                                 owner=self.user1)
        # /user1/file1
        with open('manage.py', 'rb') as f:
            File.objects.create(my_file=DjangoFile(f),
                                parent=self.user1.home_directory,
                                name='file1')

        none_dir = Directory.objects.create(name='NONE',
                                            parent=self.user2.home_directory,
                                            access_type=AccessType.NONE,
                                            owner=self.user2)
        with open('manage.py', 'rb') as f:
            File.objects.create(my_file=DjangoFile(f),
                                parent=none_dir,
                                name='file')
        all_dir = Directory.objects.create(name='ALL',
                                           parent=self.user2.home_directory,
                                           access_type=AccessType.ALL,
                                           owner=self.user2)
        with open('manage.py', 'rb') as f:
            File.objects.create(my_file=DjangoFile(f),
                                parent=all_dir,
                                name='file')
        for_user1_dir = Directory.objects.create(name='FOR_USER1',
                                                 parent=self.user2.home_directory,
                                                 access_type=AccessType.GROUP,
                                                 owner=self.user2)
        for_user1_dir.allowed_users.add(self.user1)
        for_user1_dir.save()
        with open('manage.py', 'rb') as f:
            File.objects.create(my_file=DjangoFile(f),
                                parent=for_user1_dir,
                                name='file')
        self.client = APIClient()

    def test_create_dir(self):
        self.client.force_authenticate(user=self.user1)

        # можно создать директорию у себя
        url = '/api/dir/path=/user1/'
        data = {'name': 'dir2'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # но ещё одну с таким же именем - нет
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # с "плохими" именами - нет
        data = {'name': 'dir2/dir3'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # и папку с таким же именем, как у файла - тоже нет
        data = {'name': 'file1'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # в папке, в которую нет доступа - тоже нельзя
        url = '/api/dir/path=/user2/NONE/'
        data = {'name': 'dir_from_user1'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # но в которую есть доступ - можно
        url = '/api/dir/path=/user2/ALL/'
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url = '/api/dir/path=/user2/FOR_USER1/'
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_file(self):
        self.client.force_authenticate(user=self.user1)

        # можно создать файл у себя
        url = '/api/file/path=/user1/'
        data = {
            'name': 'file',
            'my_file': open('manage.py', 'rb')
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

         # но ещё один с таким же именем - нет
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # с "плохими" именами - нет
        data.update({'name': 'dir1/file'})
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # и файл с таким же именем, как у папки - тоже нет
        data.update({'name': 'dir1'})
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # в папке, в которую нет доступа - тоже нельзя
        url = '/api/file/path=/user2/NONE/'
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # но в которую есть доступ - можно
        url = '/api/file/path=/user2/ALL/'
        data = {
            'name': 'file_from_user1',
            'my_file': open('manage.py', 'rb')
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url = '/api/file/path=/user2/FOR_USER1/'
        data = {
            'name': 'file_from_user1',
            'my_file': open('manage.py', 'rb')
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_delete_dir(self):
        self.client.force_authenticate(user=self.user1)

        url = '/api/dir/path=/user1/'
        data = {'name': 'dir2'}
        response = self.client.post(url, data)

        # удалим только что созданную директорию
        url = '/api/dir/id/{}/'.format(response.data['id'])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # удалим по несуществующему пути
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # домашнюю директорию удалять нельзя
        url = '/api/dir/path=/user1/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # чужие директории удалять тоже нельзя
        url = '/api/dir/path=/user2/NONE/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # но к которым есть доступ - можно
        url = '/api/dir/path=/user2/FOR_USER1/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_file(self):
        self.client.force_authenticate(user=self.user1)

        url = '/api/file/path=/user1/'
        data = {
            'name': 'file',
            'my_file': open('manage.py', 'rb')
        }
        response = self.client.post(url, data)

        # удалим только что созданный файл
        url = '/api/file/id/{}/'.format(response.data['id'])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # удалим по несуществующему пути
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # чужой файл
        url = '/api/file/path=/user2/NONE/file/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # но к которым есть доступ - можно
        url = '/api/file/path=/user2/FOR_USER1/file/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_ls_dir(self):
        self.client.force_authenticate(user=self.user1)

        # пробуем получить список своих файлов
        url = '/api/get/dirs/path=/user1/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # обращаемся по несуществующему адресу
        url = '/api/get/dirs/path=/userF/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # куда можно у другого пользователя
        url = '/api/get/files/path=/user2/ALL/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = '/api/get/files/path=/user2/FOR_USER1/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # куда нельзя
        url = '/api/get/files/path=/user2/NONE/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
