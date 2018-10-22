"""
Parses config options and sets up Elasticsearch client
"""
from sanic.log import logger

from config import CONFIG

from sanic import Sanic
from elasticsearch import Elasticsearch


class ElasticsearchClientService(object):

    def __init__(self, app: Sanic, loop):
        self.app = app
        self.loop = loop

        self.client: Elasticsearch = self._init_client()

    def _init_client(self) -> Elasticsearch:
        """
        Initialises the correct Elasticsearch client for the Sanic app
        :return:
        """
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

        return client

    @property
    def elasticsearch_host(self) -> str:
        """
        Returns the Elasticsearch hostname as set in the config
        :return:
        """
        return CONFIG.ELASTIC_SEARCH.server

    @property
    def elasticsearch_async_enabled(self) -> bool:
        """
        Returns whether the async Elasticsearch client is enabled
        :return:
        """
        return CONFIG.ELASTIC_SEARCH.async_enabled

    @property
    def elasticsearch_timeout(self) -> int:
        """
        Returns the configured timeout value for the Elasticsearch HTTP client
        :return:
        """
        return CONFIG.ELASTIC_SEARCH.timeout

    async def shutdown(self):
        """
        Triggers clean shutdown of async client
        :return:
        """
        import logging

        from elasticsearch_async import AsyncElasticsearch

        if isinstance(self.client, AsyncElasticsearch):
            logging.info("Triggering clean shutdown of async Elasticsearch client")
            # Manually shutdown ES connections (await if async)
            await self.client.transport.close()
            logging.info("Shutdown complete")
        else:
            logging.info("Elasticsearch client is synchronous, no shutdown tasks")
