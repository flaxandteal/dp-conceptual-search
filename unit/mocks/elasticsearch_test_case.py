import abc
import unittest
from unittest.mock import MagicMock

from unit.mocks.mock_es_client import MockElasticsearchClient
from unit.utils.elasticsearch_test_utils import ElasticsearchTestUtils


class ElasticsearchTestCase(unittest.TestCase, ElasticsearchTestUtils, abc.ABC):
    """
    A test class for working with Elasticsearch
    """

    def setUp(self):
        response = self.mock_response

        # Mock the search client
        self.mock_client = MockElasticsearchClient()
        self.mock_client.search = MagicMock(return_value=response)
