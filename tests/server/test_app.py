import os
import unittest
from server.app import create_app

os.environ['SEARCH_CONFIG'] = 'testing'


class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client

    def assert_response_code(self, request, response, code: int):
        self.assertIsNotNone(request)
        self.assertIsNotNone(response)
        self.assertIsNotNone(response.body)
        self.assertEqual(response.status, code)
