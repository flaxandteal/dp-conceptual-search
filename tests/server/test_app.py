import unittest
from server.app import create_app


class TestApp(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestApp, self).__init__(*args, **kwargs)
        self.app = create_app()
        self.client = self.app.test_client
