import unittest

from tests.integration.users import TestUsers


class TestUserCrud(TestUsers):

    def test_find_user(self):
        """
        Tests that we can find a user using the hashed and unhashed id
        :return:
        """
        request, response = self.client.get('/users/find/%s' % self.hashed_user_id)
        self.assert_response_code(request, response, 200)


if __name__ == "__main__":
    unittest.main()
