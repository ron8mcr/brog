from api.tests import MySetupTestCase
from rest_framework import status


class DirCreationTests(MySetupTestCase):
    def setUp(self):
        super(DirCreationTests, self).setUp()
        self.url = '/api/dir/'
        self.new_dir = {
            'name': 'new_dir',
            'parent': self.user1.home_directory.id
        }

    def test_create_valid_dir_in_home_dir(self):
        response = self.client.post(self.url, self.new_dir)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_duplicate_names(self):
        response = self.client.post(self.url, self.new_dir)
        response = self.client.post(self.url, self.new_dir)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_names_with_slash(self):
        self.new_dir.update({'name': 'dir1/dir2'})
        response = self.client.post(self.url, self.new_dir)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_name_with_file(self):
        self.new_dir.update({'name': 'file1'})
        response = self.client.post(self.url, self.new_dir)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_access_none(self):
        self.new_dir.update({
            'parent': self.none_dir.id
        })
        response = self.client.post(self.url, self.new_dir)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_access_all(self):
        self.new_dir.update({
            'parent': self.all_dir.id
        })
        response = self.client.post(self.url, self.new_dir)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_access_group(self):
        new_dir = self.new_dir
        self.new_dir.update({
            'parent': self.for_user1_dir.id
        })
        response = self.client.post(self.url, self.new_dir)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class DirDeletionTests(MySetupTestCase):
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
        url = self.urls['NONE_DIR']
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_access_all(self):
        url = self.urls['ALL_DIR']
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_access_group(self):
        url = self.urls['GROUP_DIR']
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class DirRenameTests(MySetupTestCase):
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
        url = self.urls['NONE_DIR']
        response = self.client.put(url, {'name': 'dir2'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_rename_access_all(self):
        url = self.urls['ALL_DIR']
        response = self.client.put(url, {'name': 'dir2'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_rename_access_group(self):
        url = self.urls['GROUP_DIR']
        response = self.client.put(url, {'name': 'dir2'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ListDirTests(MySetupTestCase):
    def test_ls_home_dir(self):
        url = '/api/dir/path/user1/list_dirs/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_ls_not_existing(self):
        url = '/api/dir/path/userF/list_dirs/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_ls_access_no(self):
        url = '{}list_dirs/'.format(self.urls['NONE_DIR'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_ls_access_all(self):
        url = '{}list_dirs/'.format(self.urls['ALL_DIR'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_ls_access_group(self):
        url = '{}list_dirs/'.format(self.urls['GROUP_DIR'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
