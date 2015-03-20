from rest_framework.test import APITestCase, APIRequestFactory, APIClient
from django.core.files import File as DjangoFile
from filesharing.models import User, AccessType, Directory, File
from rest_framework import status
from factories import UserFactory, DirFactory, FileFactory


# TODO: factory_boy
class SetUpTestEnvironmentMixin(APITestCase):
    def setUp(self):
        self.user1 = UserFactory(username='user1')
        self.user2 = UserFactory(username='user2')
        
        DirFactory.create(name='user1', owner=self.user1)
        DirFactory.create(name='user2', owner=self.user2)

        # /user1/dir1
        DirFactory.create(name='dir1',
                                 parent=self.user1.home_directory,
                                 owner=self.user1)
        # /user1/file1
        FileFactory.create(parent=self.user1.home_directory, name='file1')

        none_dir = DirFactory.create(name='NONE',
                                            parent=self.user2.home_directory,
                                            access_type=AccessType.NONE,
                                            owner=self.user2)

        FileFactory.create(parent=none_dir, name='file')
                                
        all_dir = DirFactory.create(name='ALL',
                                           parent=self.user2.home_directory,
                                           access_type=AccessType.ALL,
                                           owner=self.user2)

        FileFactory.create(parent=all_dir, name='file')
        
        for_user1_dir = Directory.objects.create(name='FOR_USER1',
                                                 parent=self.user2.home_directory,
                                                 access_type=AccessType.GROUP,
                                                 owner=self.user2)
        for_user1_dir.allowed_users.add(self.user1)
        for_user1_dir.save()

        FileFactory.create(parent=for_user1_dir, name='file')
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)

    def print_response(self, response):
        print(response.content.decode('UTF-8'))


class DirCreationTests(SetUpTestEnvironmentMixin, APITestCase):
    def setUp(self):
        super(DirCreationTests, self).setUp()
        self.url = '/api/dir/'
        self.new_dir = {
            'name': 'new_dir',
            'parent': self.user1.home_directory.id
        }

    def test_create_valid_dir_in_home_dir(self):
        """ можно создать директорию у себя """
        response = self.client.post(self.url, self.new_dir)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_duplicate_names(self):
        response = self.client.post(self.url, self.new_dir)
        response = self.client.post(self.url, self.new_dir)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_names_with_slash(self):
        new_dir = self.new_dir
        new_dir.update({'name': 'dir1/dir2'})
        response = self.client.post(self.url, new_dir)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_name_with_file(self):
        new_dir = self.new_dir
        new_dir.update({'name': 'file1'})
        response = self.client.post(self.url, new_dir)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_access_none(self):
        new_dir = self.new_dir
        new_dir.update({
            'parent': Directory.objects.get(full_path='/user2/NONE').id
        })
        response = self.client.post(self.url, new_dir)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_access_all(self):
        new_dir = self.new_dir
        new_dir.update({
            'parent': Directory.objects.get(full_path='/user2/ALL').id
        })
        response = self.client.post(self.url, new_dir)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_access_group(self):
        new_dir = self.new_dir
        new_dir.update({
            'parent': Directory.objects.get(full_path='/user2/ALL').id
        })
        response = self.client.post(self.url, new_dir)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class DirDeletionTests(SetUpTestEnvironmentMixin, APITestCase):
    def test_delete(self):
        new_dir = {
            'name': 'new_dir',
            'parent': self.user1.home_directory.id
        }
        response = self.client.post('/api/dir/', new_dir)

        # удалим только что созданную директорию
        url = '/api/dir/path/user1/new_dir/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_not_existing(self):
        response = self.client.delete('/api/dir/10000/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_home_dir(self):
        url = '/api/dir/path/user1/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_access_no(self):
        url = '/api/dir/path/user2/NONE/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_access_all(self):
        url = '/api/dir/path/user2/ALL/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_access_group(self):
        url = '/api/dir/path/user2/FOR_USER1/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class DirRenameTests(SetUpTestEnvironmentMixin, APITestCase):
    def test_rename(self):
        url = '/api/dir/path/user1/dir1/'
        response = self.client.put(url, {'name': 'dir2'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_rename_home_dir(self):
        url = '/api/dir/path/user1/'
        response = self.client.put(url, {'name': 'dir2'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_rename_same_name_as_file(self):
        url = '/api/dir/path/user1/dir1'
        response = self.client.put(url, {'name': 'file1'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rename_access_no(self):
        url = '/api/dir/path/user2/NONE'
        response = self.client.put(url, {'name': 'dir2'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_rename_access_all(self):
        url = '/api/dir/path/user2/ALL'
        response = self.client.put(url, {'name': 'dir2'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_rename_access_group(self):
        url = '/api/dir/path/user2/FOR_USER1'
        response = self.client.put(url, {'name': 'dir2'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class FileCreationTests(SetUpTestEnvironmentMixin, APITestCase):
    def setUp(self):
        super(FileCreationTests, self).setUp()
        self.url = '/api/file/'
        self.new_file = {
            'name': 'new_file',
            'parent': self.user1.home_directory.id,
            'my_file': open('manage.py', 'rb')
        }

    def test_create(self):
        response = self.client.post(self.url, self.new_file)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_duplicate_names(self):
        response = self.client.post(self.url, self.new_file)
        response = self.client.post(self.url, self.new_file)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_names_with_slash(self):
        self.new_file.update({'name': 'file1/2'})
        response = self.client.post(self.url, self.new_file)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_name_with_directory(self):
        self.new_file.update({'name': 'dir1'})
        response = self.client.post(self.url, self.new_file)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_access_none(self):
        self.new_file.update({
            'parent': Directory.objects.get(full_path='/user2/NONE').id
        })
        response = self.client.post(self.url, self.new_file)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_access_all(self):
        self.new_file.update({
            'parent': Directory.objects.get(full_path='/user2/ALL').id
        })
        response = self.client.post(self.url, self.new_file)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_access_group(self):
        self.new_file.update({
            'parent': Directory.objects.get(full_path='/user2/ALL').id
        })
        response = self.client.post(self.url, self.new_file)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class FileDeletionTests(SetUpTestEnvironmentMixin, APITestCase):
    def test_delete(self):
        new_file = {
            'name': 'new_file',
            'parent': self.user1.home_directory.id,
            'my_file': open('manage.py', 'rb')
        }
        response = self.client.post('/api/file/', new_file)

        # удалим только что созданный файл
        url = '/api/file/path/user1/new_file/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_not_existing(self):
        response = self.client.delete('/api/file/10000/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_access_no(self):
        url = '/api/file/path/user2/NONE/file/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_access_all(self):
        url = '/api/file/path/user2/ALL/file/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_access_group(self):
        url = '/api/file/path/user2/FOR_USER1/file/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class ListDirTests(SetUpTestEnvironmentMixin, APITestCase):
    def test_ls_home_dir(self):
        url = '/api/dir/path/user1/list_dirs/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_ls_not_existing(self):
        url = '/api/dir/path/userF/list_dirs/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_ls_access_no(self):
        url = '/api/dir/path/user2/NONE/list_dirs/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_ls_access_all(self):
        url = '/api/dir/path/user2/ALL/list_dirs/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_ls_access_all(self):
        url = '/api/dir/path/user2/FOR_USER1/list_dirs/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
