"""
Test class for Sanic app
"""
import os
import unittest

from server.app import create_app
from server.sanic_elasticsearch import SanicElasticsearch

os.environ['SEARCH_CONFIG'] = 'testing'


class TestApp(unittest.TestCase):
    def setUp(self):
        self._app: SanicElasticsearch = create_app()
        self._client = self._app.test_client

    @property
    def mock_client(self):
        """
        Returns a handle on the mock Elasticsearch client
        :return:
        """
        return self._app.elasticsearch.client


    @staticmethod
    def url_encode(params: dict):
        """
        Url encode a dictionary
        :param params:
        :return:
        """
        import urllib

        return urllib.parse.urlencode(params)

    def assert_response_code(self, request, response, code: int):
        self.assertIsNotNone(request, msg="request should not be none")
        self.assertIsNotNone(response, msg="response should not be none")
        self.assertIsNotNone(response.body,
                             msg="response body should not be none")
        self.assertEqual(
            response.status,
            code,
            msg="exit code should be '%d'" %
            code)

    def _route_and_check(
            self,
            method: str,
            uri: str,
            expected_code: int,
            **kwargs):
        fn = getattr(self._client, method)
        request, response = fn(uri, **kwargs)
        self.assert_response_code(request, response, expected_code)

        return request, response

    # Shorthand method decorators
    def get(self, uri: str, expected_code: int, **kwargs):
        return self._route_and_check('get', uri, expected_code, **kwargs)

    def post(self, uri: str, expected_code: int, **kwargs):
        return self._route_and_check('post', uri, expected_code, **kwargs)

    def put(self, uri: str, expected_code: int, **kwargs):
        return self._route_and_check('put', uri, expected_code, **kwargs)

    def head(self, uri: str, expected_code: int, **kwargs):
        return self._route_and_check('head', uri, expected_code, **kwargs)

    def options(self, uri: str, expected_code: int, **kwargs):
        return self._route_and_check('options', uri, expected_code, **kwargs)

    def patch(self, uri: str, expected_code: int, **kwargs):
        return self._route_and_check('patch', uri, expected_code, **kwargs)

    def delete(self, uri: str, expected_code: int, **kwargs):
        return self._route_and_check('delete', uri, expected_code, **kwargs)
