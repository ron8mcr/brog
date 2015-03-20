from rest_framework import status
from api.tests import MySetupTestCase
from tempfile import NamedTemporaryFile


class FileCreationTests(MySetupTestCase):
    def setUp(self):
        super(FileCreationTests, self).setUp()
        self.url = '/api/file/'
        my_file = NamedTemporaryFile()
        my_file.write(b'something')
        my_file.seek(0)
        self.new_file = {
            'name': 'new_file',
            'parent': self.user1.home_directory.id,
            'my_file': my_file
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
            'parent': self.none_dir.id
        })
        response = self.client.post(self.url, self.new_file)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_access_all(self):
        self.new_file.update({
            'parent': self.all_dir.id
        })
        response = self.client.post(self.url, self.new_file)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_access_group(self):
        self.new_file.update({
            'parent': self.all_dir.id
        })
        response = self.client.post(self.url, self.new_file)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class FileDeletionTests(MySetupTestCase):
    def test_delete(self):
        my_file = NamedTemporaryFile()
        my_file.write(b'something')
        my_file.seek(0)
        new_file = {
            'name': 'new_file',
            'parent': self.user1.home_directory.id,
            'my_file': my_file
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
