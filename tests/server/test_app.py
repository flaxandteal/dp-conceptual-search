import os
import unittest
from server.app import create_app

os.environ['SEARCH_CONFIG'] = 'testing'
os.environ['MONGO_BIND_ADDR'] = 'mongodb://0.0.0.0:27017'
os.environ['MONGO_SEARCH_DATABASE'] = 'test'


class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client

    def assert_response_code(self, request, response, code: int):
        self.assertIsNotNone(request)
        self.assertIsNotNone(response)
        self.assertIsNotNone(response.body)
        self.assertEqual(response.status, code)
