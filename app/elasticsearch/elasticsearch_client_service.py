"""
Parses config options and sets up Elasticsearch client
"""
from sanic.log import logger

from config import ELASTIC_SEARCH_CONFIG

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
        from unit.elasticsearch.elasticsearch_test_case import ElasticsearchTestCase

        test_utils = ElasticsearchTestCase()

        response = test_utils.mock_response
        health_response = test_utils.mock_health_response

        # Mock the search client
        self._client = MockElasticsearchClient()
        self._client.search = MagicMock(return_value=response)

        # Mock the cluster health API
        self._client.cluster.health = MagicMock(return_value=health_response)

    def _init_client(self):
        """
        Initialises the correct Elasticsearch client for the Sanic app
        :return:
        """
        if self.app.config.get("TESTING", False):
            logger.warning("Test environment active, using MockElasticSearch client")
            self._mock_client()
        else:
            es_host = self.elasticsearch_host

            if self.elasticsearch_async_enabled:
                from elasticsearch_async import AsyncElasticsearch

                client = AsyncElasticsearch(
                    es_host, loop=self.loop, timeout=self.elasticsearch_timeout
                )
            else:
                client = Elasticsearch(
                    es_host, timeout=self.elasticsearch_timeout
                )

            self._client = client

    @property
    def elasticsearch_host(self) -> str:
        """
        Returns the Elasticsearch hostname as set in the config
        :return:
        """
        return ELASTIC_SEARCH_CONFIG.server

    @property
    def elasticsearch_async_enabled(self) -> bool:
        """
        Returns whether the async Elasticsearch client is enabled
        :return:
        """
        return ELASTIC_SEARCH_CONFIG.async_enabled

    @property
    def elasticsearch_timeout(self) -> int:
        """
        Returns the configured timeout value for the Elasticsearch HTTP client
        :return:
        """
        return ELASTIC_SEARCH_CONFIG.timeout

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
