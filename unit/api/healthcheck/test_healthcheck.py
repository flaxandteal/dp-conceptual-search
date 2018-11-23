"""
Tests the healthcheck API correctly calls the underlying Elasticsearch client
"""
from unittest import mock
from unittest.mock import MagicMock

from unit.utils.search_test_app import SearchTestApp

from unit.elasticsearch.elasticsearch_test_utils import mock_health_response, MockElasticsearchClient

from dp_fasttext.client.testing.mock_client import MockClient, mock_fasttext_client

from dp_conceptual_search.ons.conceptual.client import FastTextClientService

from dp_conceptual_search.config.config import SEARCH_CONFIG
from dp_conceptual_search.api.healthcheck.routes import Service, HealthCheckResponse
from dp_conceptual_search.app.elasticsearch.elasticsearch_client_service import ElasticsearchClientService


def mock_indices_exists_client(*args):
    """
    Mocks a True result for the indices.exists API
    :param args:
    :return:
    """
    health_response = mock_health_response("green")

    mock_client = MockElasticsearchClient()

    mock_client.cluster.health = MagicMock(return_value=health_response)
    mock_client.indices.exists = MagicMock(return_value=True)

    return mock_client


def mock_indices_not_exists_client(*args):
    """
    Mocks a True result for the indices.exists API
    :param args:
    :return:
    """
    health_response = mock_health_response("green")

    mock_client = MockElasticsearchClient()

    mock_client.cluster.health = MagicMock(return_value=health_response)
    mock_client.indices.exists = MagicMock(return_value=False)

    return mock_client


def mock_health_check_client_green(*args):
    """
    Returns a mock Elasticsearch client for healthchecks with a cluster status of 'green'
    :return:
    """
    # Mock search response
    health_response = mock_health_response("green")

    # Mock the search client
    mock_client = MockElasticsearchClient()
    mock_client.cluster.health = MagicMock(return_value=health_response)
    mock_client.indices.exists = MagicMock(return_value=True)

    return mock_client


def mock_health_check_client_yellow(*args):
    """
    Returns a mock Elasticsearch client for healthchecks with a cluster status of 'yellow'
    :return:
    """
    # Mock search response
    health_response = mock_health_response("yellow")

    # Mock the search client
    mock_client = MockElasticsearchClient()
    mock_client.cluster.health = MagicMock(return_value=health_response)
    mock_client.indices.exists = MagicMock(return_value=True)

    return mock_client


def mock_health_check_client_red(*args):
    """
    Returns a mock Elasticsearch client for healthchecks with a cluster status of 'red'
    :return:
    """
    # Mock search response
    health_response = mock_health_response("red")

    # Mock the search client
    mock_client = MockElasticsearchClient()
    mock_client.cluster.health = MagicMock(return_value=health_response)
    mock_client.indices.exists = MagicMock(return_value=True)

    return mock_client


def mock_health_check_client_exception(*args):
    """
    Returns a mock Elasticsearch client for healthchecks which raises an exception on call
    :return:
    """
    # Mock the search client
    mock_client = MockElasticsearchClient()
    mock_client.cluster.health = MagicMock()
    mock_client.cluster.health.side_effect = Exception("Mock exception")
    mock_client.indices.exists = MagicMock(return_value=True)

    return mock_client


def raise_exception():
    """
    Simple method to raise an exception
    :return:
    """
    raise Exception("Mock exception")


def mock_unhealthy_fasttext_client():
    """
    Mocks an unhealthy dp-fasttext client
    :return:
    """
    # Initialise the MockClient and mock the 'get' and 'post' methods
    client = MockClient()
    client.get = MagicMock()

    # Set side effect to new method so we can preserve calling arguments
    client.get.side_effect = raise_exception

    return client


class HealthCheckTestCase(SearchTestApp):

    def setUp(self):
        super(HealthCheckTestCase, self).setUp()

    @mock.patch.object(FastTextClientService, 'get_fasttext_client', mock_fasttext_client)
    @mock.patch.object(ElasticsearchClientService, '_init_client', mock_health_check_client_green)
    def test_healthcheck_green(self):
        """
        Tests that the healthcheck makes the correct client call for a cluster health status of 'green'
        :return:
        """
        # Build the target URL
        target = "/healthcheck"

        # Make the request
        request, response = self.get(target, 200)
        expected_response = HealthCheckResponse()
        expected_response.set_response_for_service(Service.elasticsearch, "available", 200)
        expected_response.set_response_for_service(Service.dp_fasttext, "available", 200)

        expected_response = expected_response.to_dict()

        # Check the mock client was called with the correct arguments
        # Assert search was called with correct arguments
        self.mock_client.cluster.health.assert_called_with()

        # Check the response JSON matches the mock response
        self.assertTrue(hasattr(response, "json"), "response should contain JSON property")

        response_json = response.json
        self.assertIsNotNone(response_json, "response json should not be none")
        self.assertIsInstance(response_json, dict, "response json should be instanceof dict")

        self.assertEqual(response_json, expected_response, "returned JSON should match mock response")

    @mock.patch.object(FastTextClientService, 'get_fasttext_client', mock_fasttext_client)
    @mock.patch.object(ElasticsearchClientService, '_init_client', mock_health_check_client_yellow)
    def test_healthcheck_yellow(self):
        """
        Tests that the healthcheck makes the correct client call for a cluster health status of 'yellow'
        :return:
        """
        # Build the target URL
        target = "/healthcheck"

        # Make the request
        request, response = self.get(target, 200)
        expected_response = HealthCheckResponse()
        expected_response.set_response_for_service(Service.elasticsearch, "available", 200)
        expected_response.set_response_for_service(Service.dp_fasttext, "available", 200)

        expected_response = expected_response.to_dict()

        # Check the mock client was called with the correct arguments
        # Assert search was called with correct arguments
        self.mock_client.cluster.health.assert_called_with()

        # Check the response JSON matches the mock response
        self.assertTrue(hasattr(response, "json"), "response should contain JSON property")

        response_json = response.json
        self.assertIsNotNone(response_json, "response json should not be none")
        self.assertIsInstance(response_json, dict, "response json should be instanceof dict")

        self.assertEqual(response_json, expected_response, "returned JSON should match mock response")

    @mock.patch.object(FastTextClientService, 'get_fasttext_client', mock_fasttext_client)
    @mock.patch.object(ElasticsearchClientService, '_init_client', mock_health_check_client_red)
    def test_healthcheck_red(self):
        """
        Tests that the healthcheck makes the correct client call for a cluster health status of 'red'
        :return:
        """
        # Build the target URL
        target = "/healthcheck"

        # Make the request
        request, response = self.get(target, 500)
        expected_response = HealthCheckResponse()
        expected_response.set_response_for_service(Service.elasticsearch, "cluster unhealthy [status=red]", 500)
        expected_response.set_response_for_service(Service.dp_fasttext, "available", 200)

        expected_response = expected_response.to_dict()

        # Check the mock client was called with the correct arguments
        # Assert search was called with correct arguments
        self.mock_client.cluster.health.assert_called_with()

        # Check the response JSON matches the mock response
        self.assertTrue(hasattr(response, "json"), "response should contain JSON property")

        response_json = response.json
        self.assertIsNotNone(response_json, "response json should not be none")
        self.assertIsInstance(response_json, dict, "response json should be instanceof dict")

        self.assertEqual(response_json, expected_response, "returned JSON should match mock response")

    @mock.patch.object(FastTextClientService, 'get_fasttext_client', mock_fasttext_client)
    @mock.patch.object(ElasticsearchClientService, '_init_client', mock_health_check_client_exception)
    def test_healthcheck_exception(self):
        """
        Tests that the healthcheck API returns a 500 with the correct response body when an exception is raised
        by the client
        :return:
        """
        # Build the target URL
        target = "/healthcheck"

        # Make the request
        request, response = self.get(target, 500)
        expected_response = HealthCheckResponse()
        expected_response.set_response_for_service(Service.elasticsearch, "unreachable", 500)
        expected_response.set_response_for_service(Service.dp_fasttext, "available", 200)

        expected_response = expected_response.to_dict()

        # Check the mock client was called with the correct arguments
        # Assert search was called with correct arguments
        self.mock_client.cluster.health.assert_called_with()

        # Check the response JSON matches the mock response
        self.assertTrue(hasattr(response, "json"), "response should contain JSON property")

        response_json = response.json
        self.assertIsNotNone(response_json, "response json should not be none")
        self.assertIsInstance(response_json, dict, "response json should be instanceof dict")

        self.assertEqual(response_json, expected_response, "returned JSON should match mock response")

    @mock.patch.object(FastTextClientService, 'get_fasttext_client', mock_fasttext_client)
    @mock.patch.object(ElasticsearchClientService, '_init_client', mock_indices_exists_client)
    def test_indices_exist(self):
        """
        Tests that the healthcheck API returns a 200 OK when indices exist
        :return:
        """
        # Build the target URL
        target = "/healthcheck"

        indices = "{ons},{departments}".format(ons=SEARCH_CONFIG.search_index,
                                               departments=SEARCH_CONFIG.departments_search_index)

        # Make the request
        request, response = self.get(target, 200)
        expected_response = HealthCheckResponse()
        expected_response.set_response_for_service(Service.elasticsearch, "available", 200)
        expected_response.set_response_for_service(Service.dp_fasttext, "available", 200)

        expected_response = expected_response.to_dict()

        # Check the mock client was called with the correct arguments
        # Assert search was called with correct arguments
        self.mock_client.indices.exists.assert_called_with(indices)

        # Check the response JSON matches the mock response
        self.assertTrue(hasattr(response, "json"), "response should contain JSON property")

        response_json = response.json
        self.assertIsNotNone(response_json, "response json should not be none")
        self.assertIsInstance(response_json, dict, "response json should be instanceof dict")

        self.assertEqual(response_json, expected_response, "returned JSON should match mock response")

    @mock.patch.object(FastTextClientService, 'get_fasttext_client', mock_fasttext_client)
    @mock.patch.object(ElasticsearchClientService, '_init_client', mock_indices_not_exists_client)
    def test_indices_do_not_exist(self):
        """
        Tests that the healthcheck API returns a 500 INTERNAL_SERVER_ERROR when indices DO NOT exist
        :return:
        """
        # Build the target URL
        target = "/healthcheck"

        indices = "{ons},{departments}".format(ons=SEARCH_CONFIG.search_index,
                                               departments=SEARCH_CONFIG.departments_search_index)

        # Make the request
        request, response = self.get(target, 500)
        expected_response = HealthCheckResponse()
        expected_response.set_response_for_service(Service.elasticsearch, "indices unavailable [indices={indices}]"
                                                   .format(indices=indices), 500)
        expected_response.set_response_for_service(Service.dp_fasttext, "available", 200)

        expected_response = expected_response.to_dict()

        # Check the mock client was called with the correct arguments
        # Assert search was called with correct arguments
        self.mock_client.indices.exists.assert_called_with(indices)

        # Check the response JSON matches the mock response
        self.assertTrue(hasattr(response, "json"), "response should contain JSON property")

        response_json = response.json
        self.assertIsNotNone(response_json, "response json should not be none")
        self.assertIsInstance(response_json, dict, "response json should be instanceof dict")

        self.assertEqual(response_json, expected_response, "returned JSON should match mock response")

    @mock.patch.object(FastTextClientService, 'get_fasttext_client', mock_unhealthy_fasttext_client)
    @mock.patch.object(ElasticsearchClientService, '_init_client', mock_health_check_client_green)
    def test_fasttext_unhealthy(self):
        """
        Tests that the healthcheck API returns a 500 INTERNAL_SERVER_ERROR when dp-fasttext is unhealty
        :return:
        """
        # Build the target URL
        target = "/healthcheck"

        indices = "{ons},{departments}".format(ons=SEARCH_CONFIG.search_index,
                                               departments=SEARCH_CONFIG.departments_search_index)

        # Make the request
        request, response = self.get(target, 500)
        expected_response = HealthCheckResponse()
        expected_response.set_response_for_service(Service.elasticsearch, "available", 200)
        expected_response.set_response_for_service(Service.dp_fasttext, "unreachable", 500)

        expected_response = expected_response.to_dict()

        # Check the mock client was called with the correct arguments
        # Assert search was called with correct arguments
        self.mock_client.indices.exists.assert_called_with(indices)

        # Check the response JSON matches the mock response
        self.assertTrue(hasattr(response, "json"), "response should contain JSON property")

        response_json = response.json
        self.assertIsNotNone(response_json, "response json should not be none")
        self.assertIsInstance(response_json, dict, "response json should be instanceof dict")

        self.assertEqual(response_json, expected_response, "returned JSON should match mock response")
