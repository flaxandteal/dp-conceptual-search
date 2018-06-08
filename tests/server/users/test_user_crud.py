import unittest
from tests.server.test_app import TestApp

from uuid import uuid1


class TestUsers(TestApp):
    def __init__(self, *args, **kwargs):
        super(TestUsers, self).__init__(*args, **kwargs)

        # Generate a test user id
        self.user_id = str(uuid1())

    def setUp(self):
        """
        Tests that we can create a user
        :return:
        """
        from server.users.user import User

        cookies = {User.user_id_key: self.user_id}
        request, response = self.client.put('/users/create', cookies=cookies)

        self.assert_response_code(request, response, 200)

    def test_find_user(self):
        """
        Tests that we can find a user using both the hashed and unhashed id
        :return:
        """
        from server.anonymize import hash_value

        request, response = self.client.get('/users/find/%s' % self.user_id)
        self.assert_response_code(request, response, 200)

        # Hash value
        request, response = self.client.get('/users/find/%s' % hash_value(self.user_id))
        self.assert_response_code(request, response, 200)

    def tearDown(self):
        """
        Deletes the user we created
        :return:
        """
        from server.anonymize import hash_value

        request, response = self.client.delete('/users/delete/%s' % self.user_id)

        self.assert_response_code(request, response, 200)

        # Make sure we can no longer find the user

        request, response = self.client.get('/users/find/%s' % self.user_id)
        self.assert_response_code(request, response, 404)

        request, response = self.client.get('/users/find/%s' % hash_value(self.user_id))
        self.assert_response_code(request, response, 404)


if __name__ == "__main__":
    unittest.main()
