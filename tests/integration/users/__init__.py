import unittest
from tests.server.test_app import TestApp

from uuid import uuid1


class TestUsers(TestApp):
    def __init__(self, *args, **kwargs):
        super(TestUsers, self).__init__(*args, **kwargs)

        # Generate a test user id
        self.user_id = str(uuid1())

    @property
    def hashed_user_id(self):
        from server.anonymize import hash_value
        return hash_value(self.user_id)

    def setUp(self):
        """
        Tests that we can create a user
        :return:
        """
        super(TestUsers, self).setUp()

        from server.users.user import User

        cookies = {User.user_id_key: self.user_id}
        self.put('/users/create', 200, cookies=cookies)

    def tearDown(self):
        """
        Deletes the user we created
        :return:
        """
        # Delete and assert 200 OK
        self.delete('/users/delete/%s' % self.hashed_user_id, 200)

        # Make sure we can no longer find the user

        self.get('/users/find/%s' % self.user_id, 404)
        self.get('/users/find/%s' % self.hashed_user_id, 404)


if __name__ == "__main__":
    unittest.main()
