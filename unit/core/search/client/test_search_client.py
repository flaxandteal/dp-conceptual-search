import asyncio
import unittest
from unittest.mock import MagicMock

from core.search.client import SearchClient


class SearchClientTestCase(unittest.TestCase):

    def setUp(self):
        from unit.core.search.client.mock_es_client import MockElasticsearchClient

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

    @property
    def test_body(self):
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

    def test_search_called(self):
        """
        Tests that search was called with correct arguments
        :return:
        """
        event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(event_loop)

        async def run_test():
            client: SearchClient = self.get_client()

            # Call search and check arguments match those provided
            client.update_from_dict(self.test_body)

            response = await client.execute(ignore_cache=True)

            self.mock_client.search.assert_called_with(index=[self.index], doc_type=[], body=self.test_body,)

        # Run the async test
        coro = asyncio.coroutine(run_test)
        event_loop.run_until_complete(coro())
        event_loop.close()

