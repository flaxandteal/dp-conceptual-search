import unittest
from server.app import create_app


class TestApp(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestApp, self).__init__(*args, **kwargs)
        import os

        os.environ['SEARCH_CONFIG'] = 'testing'
        self.app = create_app()
        self.client = self.app.test_client

    def assert_response_code(self, request, response, code: int):
        self.assertIsNotNone(request)
        self.assertIsNotNone(response)
        self.assertIsNotNone(response.body)
        self.assertEqual(response.status, code)
