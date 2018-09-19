"""
Parses config options and sets up Elasticsearch client
"""
import os

import logging

from sanic import Sanic
from elasticsearch import Elasticsearch


class ElasticsearchClientService(object):

    def __init__(self, app: Sanic, loop):
        self.app = app
        self.loop = loop

        self._client = None
        self._init_client()

    def _mock_client(self):
        """
        Mocks an Elasticsearch client for testing
        :return:
        """
        from unittest.mock import MagicMock
        from unit.mocks.mock_es_client import MockElasticsearchClient
        from unit.utils.elasticsearch_test_utils import ElasticsearchTestUtils

        test_utils = ElasticsearchTestUtils()

        hits = test_utils.mock_hits()

        response = {
            "_shards": test_utils.mock_shards_json,
            "hits": {
                "hits": hits,
                "max_score": 1.0,
                "total": len(hits)
            },
            "timed_out": test_utils.mock_timed_out,
            "took": test_utils.mock_took
        }

        # Mock the search client
        self._client = MockElasticsearchClient()
        self._client.search = MagicMock(return_value=response)

    def _init_client(self):
        """
        Initialises the correct Elasticsearch client for the Sanic app
        :return:
        """
        if self.app.config.get("TESTING", False):
            logging.warning("Test environment active, using MockElasticSearch client")
            self._mock_client()
        else:
            es_host = self.get_search_url()

            if self.async_enabled():
                from elasticsearch_async import AsyncElasticsearch

                logging.info("Initialising asynchronous Elasticsearch client with host {0}".format(es_host))
                client = AsyncElasticsearch(
                    es_host, loop=self.loop, timeout=self.get_search_timeout()
                )
            else:
                logging.info("Initialising synchronous Elasticsearch client with host {0}".format(es_host))
                client = Elasticsearch(
                    es_host, timeout=self.get_search_timeout()
                )

            self._client = client

    def get_search_url(self) -> str:
        """
        Parse env var to determine Elasticsearch host address
        :return:
        """
        return self.app.config.get("ELASTIC_SEARCH_SERVER")

    def get_search_timeout(self) -> int:
        """
        Parse env var to determine Elasticsearch Timeout value in ms
        :return:
        """
        return self.app.config.get("ELASTIC_SEARCH_TIMEOUT")

    def async_enabled(self) -> bool:
        """
        Parse env var to determine if the async client is enabled
        :return:
        """
        return self.app.config.get("ELASTIC_SEARCH_ASYNC_ENABLED")

    @property
    def client(self) -> Elasticsearch:
        """
        Parse config options and return correct client
        :return:
        """
        if self._client is None:
            self._init_client()

        return self._client

    async def shutdown(self):
        """
        Triggers clean shutdown of async client
        :return:
        """
        import logging

        from elasticsearch_async import AsyncElasticsearch

        if isinstance(self._client, AsyncElasticsearch):
            logging.info("Triggering clean shutdown of async Elasticsearch client")
            # Manually shutdown ES connections (await if async)
            await self._client.transport.close()
            logging.info("Shutdown complete")
        else:
            logging.info("Elasticsearch client is synchronous, no shutdown tasks")
