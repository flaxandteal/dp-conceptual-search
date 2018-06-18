import unittest
import numpy as np

from uuid import uuid1

from tests.integration.users import TestUsers


class TestUserRecommendation(TestUsers):
    session_id = str(uuid1())
    search_term = "rpi"
    search_term_negative = "crime"

    @property
    def cookies(self):
        from server.users.user import User
        from server.users.session import Session

        cookies = {User.user_id_key: self.user_id,
                   Session.session_id_key: self.session_id}
        return cookies

    def test_update_user(self):
        """
        Tests that we can find a user using the hashed  id
        :return:
        """
        # Find the user
        request, response = self.get('/users/find/%s' % self.hashed_user_id, 200)

        # Assert user vector is in json response
        self.assertTrue(hasattr(response, "json"))
        self.assertIsNotNone(response.json)

        doc = response.json
        self.assertIsInstance(doc, dict)
        self.assertIn('user_vector', doc)

        # Make sure vector is None (we haven't updated it yet)
        user_vector = doc['user_vector']
        self.assertIsNone(user_vector)

        # Update the user (positive)
        request, response = self.post('/recommend/update/positive/%s' % self.search_term, 200, cookies=self.cookies)

        # Assert user vector is in json response
        self.assertTrue(hasattr(response, "json"))
        self.assertIsNotNone(response.json)

        doc = response.json
        self.assertIsInstance(doc, dict)
        self.assertIn('user_vector', doc)

        user_vector = doc['user_vector']
        self.assertIsInstance(user_vector, list)
        self.assertIsNotNone(user_vector)

        # Assert NOT all zeros
        user_array = np.array(user_vector)
        self.assertFalse(np.all(user_array == 0))

        # Update the user (negative)
        request, response = self.post('/recommend/update/negative/%s' % self.search_term_negative, 200, cookies=self.cookies)

        # Assert user vector is in json response
        self.assertTrue(hasattr(response, "json"))
        self.assertIsNotNone(response.json)

        doc = response.json
        self.assertIsInstance(doc, dict)
        self.assertIn('user_vector', doc)

        new_user_vector = doc['user_vector']
        self.assertIsInstance(new_user_vector, list)
        self.assertIsNotNone(new_user_vector)

        # Assert NOT all zeros
        new_user_vector = np.array(new_user_vector)
        self.assertFalse(np.all(new_user_vector == 0))

        # Assert not the same as previous vector
        self.assertFalse((new_user_vector == user_vector).all())


if __name__ == "__main__":
    unittest.main()
