import abc
import unittest
from unittest.mock import MagicMock


class ElasticsearchTestCase(unittest.TestCase, abc.ABC):
    """
    A test class for working with Elasticsearch
    """

    def setUp(self):
        from unit.utils.mock_es_client import MockElasticsearchClient

        hit = {
            "_id": "test_hit",
            "_source": {
                "name": "Randy Marsh",
                "occupation": "Receptionist at Tom's Rhinoplasty"
            }
        }

        # Mock the search client
        self.mock_client = MockElasticsearchClient()
        self.mock_client.search = MagicMock(return_value=hit)
