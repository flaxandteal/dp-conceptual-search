import unittest

from tests.server.users import TestUsers


class TestUserCrud(TestUsers):

    def test_find_user(self):
        """
        Tests that we can find a user using both the hashed and unhashed id
        :return:
        """
        from server.anonymize import hash_value

        request, response = self.client.get('/users/find/%s' % self.user_id)
        self.assert_response_code(request, response, 200)

        # Hash value
        request, response = self.client.get(
            '/users/find/%s' %
            hash_value(
                self.user_id))
        self.assert_response_code(request, response, 200)


if __name__ == "__main__":
    unittest.main()
