import unittest
from tests.server.test_app import TestApp


class SearchTestSuite(TestApp):

    def test_valid_search_returns_200(self):
        """
        Test that a valid search query returns a 200 OK response.
        :return:
        """
        request, response = self.client.post('/search/ons?q=rpi')

        self.assert_response_code(request, response, 200)

        self.assertIsNotNone(response.json)
        self.assertIsInstance(response.json, dict)

        expected_keys = ['result', 'counts', 'featuredResult']
        for key in expected_keys:
            self.assertTrue(key in response.json)
            self.assertIsNotNone(response.json[key])
            self.assertIsInstance(response.json[key], dict)
            self.assertGreater(len(response.json[key]), 0)

    def test_invalid_search_returns_400(self):
        """
        Test that not specifying a query term raises a 400 BAD_REQUEST for the primary search method.
        :return:
        """
        request, response = self.client.post('/search/ons')

        self.assertIsNotNone(request)
        self.assertIsNotNone(response)
        self.assertIsNotNone(response.body)
        self.assertEqual(response.status, 400)

    def test_valid_search_data_returns_200(self):
        """
        Test that a valid search data query returns a 200 OK response.
        :return:
        """
        request, response = self.client.post('/search/ons/data?q=rpi')

        self.assert_response_code(request, response, 200)

        self.assertIsNotNone(response.json)
        self.assertIsInstance(response.json, dict)

        expected_keys = ['result', 'counts', 'featuredResult']
        for key in expected_keys:
            self.assertTrue(key in response.json)
            self.assertIsNotNone(response.json[key])
            self.assertIsInstance(response.json[key], dict)
            self.assertGreater(len(response.json[key]), 0)

    def test_invalid_search_data_returns_400(self):
        """
        Test that not specifying a query term raises a 400 BAD_REQUEST for search data.
        :return:
        """
        request, response = self.client.post('/search/ons/data')

        self.assert_response_code(request, response, 400)

    def test_valid_search_publications_returns_200(self):
        """
        Test that a valid search publications query returns a 200 OK response.
        :return:
        """
        request, response = self.client.post('/search/ons/publications?q=rpi')

        self.assert_response_code(request, response, 200)

        self.assertIsNotNone(response.json)
        self.assertIsInstance(response.json, dict)

        expected_keys = ['result', 'counts', 'featuredResult']
        for key in expected_keys:
            self.assertTrue(key in response.json)
            self.assertIsNotNone(response.json[key])
            self.assertIsInstance(response.json[key], dict)
            self.assertGreater(len(response.json[key]), 0)

    def test_invalid_search_publications_returns_400(self):
        """
        Test that not specifying a query term raises a 400 BAD_REQUEST for search publications.
        :return:
        """
        request, response = self.client.post('/search/ons/publications')

        self.assert_response_code(request, response, 400)

    def test_valid_search_departments_returns_200(self):
        """
        Test that a valid search against the departments index returns a 200 OK response.
        :return:
        """
        request, response = self.client.post('/search/ons/departments?q=rpi')

        self.assert_response_code(request, response, 200)

        self.assertIsNotNone(response.json)
        self.assertIsInstance(response.json, dict)

        expected_keys = ['numberOfResults', 'took', 'results']
        for key in expected_keys:
            self.assertTrue(key in response.json)
            self.assertIsNotNone(response.json[key])

    def test_invalid_search_departments_returns_400(self):
        """
        Test that not specifying a query term raises a 400 BAD_REQUEST against the departments index.
        :return:
        """
        request, response = self.client.post('/search/ons/departments')

        self.assert_response_code(request, response, 400)


if __name__ == "__main__":
    unittest.main()
