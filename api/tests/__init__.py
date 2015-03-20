from rest_framework.test import APITestCase, APIClient
from filesharing.models import AccessType
from api.factories import UserFactory, DirFactory, FileFactory


class MySetupTestCase(APITestCase):
    def setUp(self):
        self.user1 = UserFactory(username='user1')
        user2 = UserFactory(username='user2')

        DirFactory.create(name='user1', owner=self.user1)
        DirFactory.create(name='user2', owner=user2)

        # /user1/dir1
        DirFactory.create(name='dir1',
                          parent=self.user1.home_directory,
                          owner=self.user1)
        # /user1/file1
        FileFactory.create(parent=self.user1.home_directory, name='file1')

        self.none_dir = DirFactory.create(name='NONE',
                                          parent=user2.home_directory,
                                          access_type=AccessType.NONE,
                                          owner=user2)
        FileFactory.create(parent=self.none_dir, name='file')

        self.all_dir = DirFactory.create(name='ALL',
                                         parent=user2.home_directory,
                                         access_type=AccessType.ALL,
                                         owner=user2)
        FileFactory.create(parent=self.all_dir, name='file')

        self.for_user1_dir = DirFactory.create(name='FOR_USER1',
                                               parent=user2.home_directory,
                                               access_type=AccessType.GROUP,
                                               owner=user2)
        self.for_user1_dir.allowed_users.add(self.user1)
        self.for_user1_dir.save()
        FileFactory.create(parent=self.for_user1_dir, name='file')

        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)
        self.urls = {
            'ALL_DIR': '/api/dir/path/user2/ALL/',
            'NONE_DIR': '/api/dir/path/user2/NONE/',
            'GROUP_DIR': '/api/dir/path/user2/FOR_USER1/'
        }

    def print_response(self, response):
        print(response.content.decode('UTF-8'))
