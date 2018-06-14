import os
import unittest
from server.app import create_app

os.environ['SEARCH_CONFIG'] = 'testing'


class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client

    def assert_response_code(self, request, response, code: int):
        self.assertIsNotNone(request, msg="request should not be none")
        self.assertIsNotNone(response, msg="response should not be none")
        self.assertIsNotNone(response.body, msg="response body should not be none")
        self.assertEqual(response.status, code, msg="exit code should be '%d'" % code)
