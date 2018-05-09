import unittest
from tests.server.test_app import TestApp


class SearchTestSuite(TestApp):

    def test_valid_search_returns_200(self):
        request, response = self.client.post('/search/ons?q=rpi')

        self.assertIsNotNone(request)
        self.assertIsNotNone(response)
        self.assertIsNotNone(response.body)
        self.assertEqual(response.status, 200)

    def test_invalid_search_returns_400(self):
        request, response = self.client.post('/search/ons')

        self.assertIsNotNone(request)
        self.assertIsNotNone(response)
        self.assertIsNotNone(response.body)
        self.assertEqual(response.status, 400)


if __name__ == "__main__":
    unittest.main()
