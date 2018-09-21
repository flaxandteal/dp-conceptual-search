"""
Test class for Sanic app
"""
import unittest

from urllib import parse as urllib_parse

from server.app import create_app
from server.request.ons_request import ONSRequest
from server.sanic_elasticsearch import SanicElasticsearch


class TestApp(unittest.TestCase):
    def setUp(self):
        """
        Initialises the Sanic app and test client
        :return:
        """
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
        return urllib_parse.urlencode(params)

    def assert_response_code(self, request, response, code: int):
        """
        Assert a response has the correct response code
        :param request:
        :param response:
        :param code:
        :return:
        """
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
        """
        Routes the request via the test client and makes basic assertions, including status code and request ID
        :param method:
        :param uri:
        :param expected_code:
        :param kwargs:
        :return:
        """
        fn = getattr(self._client, method)

        request, response = fn(uri, **kwargs)

        # Assert correct response code
        self.assert_response_code(request, response, expected_code)

        # Assert request object has a request ID
        self.assertIsInstance(request, ONSRequest, "request should be instance of ONSRequest")
        self.assertTrue(hasattr(request, "request_id"), "request should have request_id attribute")
        self.assertIsNotNone(request.request_id, "request_id should not be none")
        self.assertIsInstance(request.request_id, str, "request_id should be instance of string")

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
