import unittest
import numpy as np

from uuid import uuid1

from tests.server.users import TestUsers


class TestUserRecommendation(TestUsers):
    session_id = str(uuid1())
    search_term = "rpi"

    @property
    def cookies(self):
        from server.users.user import User
        from server.users.session import Session

        cookies = {User.user_id_key: self.user_id,
                   Session.session_id_key: self.session_id}
        return cookies

    def test_update_user(self):
        """
        Tests that we can find a user using both the hashed and unhashed id
        :return:
        """
        # Find the user
        request, response = self.client.get('/users/find/%s' % self.user_id)
        self.assert_response_code(request, response, 200)

        # Assert user vector is in json response
        self.assertTrue(hasattr(response, "json"))
        self.assertIsNotNone(response.json)

        doc = response.json
        self.assertIsInstance(doc, dict)
        self.assertTrue('user_vector' in doc)

        # Make sure vector is None
        user_vector = doc['user_vector']
        self.assertIsNone(user_vector)

        # Update the user
        request, response = self.client.post(
            '/users/update/%s' %
            self.search_term, cookies=self.cookies)
        self.assert_response_code(request, response, 200)

        # Assert user vector is in json response
        self.assertTrue(hasattr(response, "json"))
        self.assertIsNotNone(response.json)

        doc = response.json
        self.assertIsInstance(doc, dict)
        self.assertTrue('user_vector' in doc)

        user_vector = doc['user_vector']
        self.assertIsInstance(user_vector, list)
        self.assertIsNotNone(user_vector)

        # import time
        # while True:
        #     print("This prints once a minute.")
        #     time.sleep(60)  # Delay for 1 minute (60 seconds).

        # Assert NOT all zeros
        user_array = np.array(user_vector)
        self.assertFalse(np.all(user_array == 0))


if __name__ == "__main__":
    unittest.main()
