from core.search.client.search_client import SearchClient
from ons.search.client.search_engine import SearchEngine

from unit.utils.elasticsearch_test_case import ElasticsearchTestCase


class SearchEngineTestCase(ElasticsearchTestCase):
    """
    Unit test for ONS SearchEngine class

    """
    @property
    def get_body(self):
        """
        Test query body
        :return:
        """
        body = {
            "query": {
                "match": {
                    "name": "Randy Marsh"
                }
            }
        }
        return body

    @property
    def index(self):
        """
        Returns the test index
        :return:
        """
        return "test"

    def get_client(self) -> SearchClient:
        """
        Create an instance of a SearchClient for testing
        :return:
        """

        client = SearchClient(using=self.mock_client, index=self.index)
        return client

    def get_search_engine(self) -> SearchEngine:
        """
        Create an instance of a SearchEngine for testing
        :return:
        """
        engine = SearchEngine(using=self.get_client(), index=self.index)
        return engine

    def test_paginate(self):
        """
        Tests that the paginate method works as expected
        :return:
        """
        import random

        # Create an instance of the SearchEngine
        engine = self.get_search_engine()

        # Generate a random page number between 1 and 10
        current_page = random.randint(1, 10)

        # Generate a random page size between 11 and 20
        size = random.randint(11, 20)

        # Call paginate
        engine = engine.paginate(current_page, size)

        # Calculate correct start page number
        from_start = 0 if current_page <= 1 else (current_page - 1) * size

        # Convert to dictionary
        engine_dict = engine.to_dict()
        self.assertIsNotNone(engine_dict, "engine dict should not be none")

        # Assert correct query structure
        expected = {
            "from": from_start,
            "query": {
                "match_all": {}
            },
            "size": size
        }

        for key in expected:
            self.assertIn(key, engine_dict, "key '{0}' should exist in engine dict".format(key))
            self.assertEqual(expected[key], engine_dict[key],
                             "value for key '{0}' should match expected value".format(key))
