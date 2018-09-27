"""
Tests the healthcheck API correctly calls the underlying Elasticsearch client
"""
from unit.utils.test_app import TestApp

from unit.elasticsearch.elasticsearch_test_case import ElasticsearchTestCase


class HealthCheckTestCase(TestApp):

    def setUp(self):
        super(HealthCheckTestCase, self).setUp()

        test_utils = ElasticsearchTestCase()
        self.mock_response = test_utils.mock_health_response

    def test_healthcheck(self):
        """
        Tests that the healthcheck makes the correct client call
        :return:
        """
        # Build the target URL
        target = "/healthcheck"

        # Make the request
        request, response = self.get(target, 200)

        # Check the mock client was called with the correct arguments
        # Assert search was called with correct arguments
        self.mock_client.cluster.health.assert_called_with()

        # Check the respons JSON matches the mock response
        self.assertTrue(hasattr(response, "json"), "response should contain JSON property")
        response_json = response.json
        self.assertIsNotNone(response_json, "response json should not be none")
        self.assertIsInstance(response_json, dict, "response json should be instanceof dict")

        self.assertEqual(response_json, self.mock_response, "returned JSON should match mock response")
