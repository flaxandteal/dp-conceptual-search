import unittest

from tests.integration.users import TestUsers


class TestUserCrud(TestUsers):

    def test_find_user(self):
        """
        Tests that we can find a user using the hashed and unhashed id
        :return:
        """
        # Make the request and assert 200 OK response
        request, response = self.get(
            '/users/find/%s' %
            self.hashed_user_id, 200)

        doc = response.json
        self.assertIsNotNone(doc, "json response must not be none")
        self.assertIsInstance(
            doc, dict, "json response must be instance of dict")

        self.assertIn("user_id", doc, "json response must contain user_id")
        self.assertIn(
            "user_vector",
            doc,
            "json response must contain user_vector")


if __name__ == "__main__":
    unittest.main()
