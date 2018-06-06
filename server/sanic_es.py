import os

from sanic import Sanic
from server.sanic_extension import SanicExtension


def get_search_url() -> str:
    search_url = os.environ.get(
        'ELASTIC_SEARCH_SERVER',
        'http://localhost:9200')
    return search_url


def get_search_timeout() -> int:
    search_timeout = int(os.environ.get('ELASTIC_SEARCH_TIMEOUT', 1000))
    return search_timeout


def async_enabled() -> bool:
    async_client_enabled = os.getenv(
        "ELASTIC_SEARCH_ASYNC_ENABLED",
        "true").lower() == "true"
    return async_client_enabled


def get_elastic_search_client(
        search_url: str,
        search_timeout: int,
        async_client: bool=False,
        **kwargs):
    """
    Initialises an Elasticsearch client. Supports asynchronous calls (must supply Sanic event loop)
    :param search_url:
    :param search_timeout:
    :param async_client:
    :param kwargs:
    :return:
    """
    from sanic.log import logger

    if async_client:
        from elasticsearch_async import AsyncElasticsearch

        logger.info(
            "Initialising async Elasticsearch client URL:%s timeout:%d" %
            (search_url, search_timeout))

        loop = kwargs.get("loop", None)
        if loop is None:
            import sys
            logger.error(
                "AsyncElasticsearch client requires the Sanic event loop!")
            sys.exit(1)

        return AsyncElasticsearch(
            search_url, loop=loop, timeout=search_timeout)
    else:
        from elasticsearch_async import Elasticsearch

        logger.info(
            "Initialising Elasticsearch client URL:%s timeout:%d" %
            (search_url, search_timeout))

        return Elasticsearch(search_url, timeout=search_timeout)


class SanicElasticsearch(SanicExtension):
    """
    Class to handle the init/tear down of ES clients for Sanic
    """

    def init_app(self, app: Sanic) -> None:
        """
        Registers init/shutdown hooks for Elasticsearch
        :param app:
        :return:
        """
        self.app = app

        @app.listener("after_server_start")
        async def elastic_search_configure(_app: Sanic, loop):
            if _app.config.get("TESTING", False) is False:
                search_url = get_search_url()
                search_timeout = get_search_timeout()
                async_client = async_enabled()

                _app.es_client = get_elastic_search_client(
                    search_url, search_timeout, async_client=async_client, loop=loop)
            else:
                from tests.server.search.test_search_client import FakeElasticsearch
                from sanic.log import logger

                logger.warn(
                    "Test client active, using FakeElasticsearch client")
                _app.es_client = FakeElasticsearch()

        @app.listener("after_server_stop")
        async def shutdown_dbs(_app: Sanic, loop):
            from elasticsearch_async import AsyncElasticsearch

            if hasattr(_app, "es_client") and \
                    hasattr(_app.es_client, "transport"):
                if hasattr(
                        _app.es_client.transport,
                        "connection_pool") and hasattr(
                        _app.es_client.transport.connection_pool,
                        "connections"):
                    # Manually shutdown ES connections (await if async)
                    for conn in _app.es_client.transport.connection_pool.connections:
                        if isinstance(_app.es_client, AsyncElasticsearch):
                            await conn.close()
                        else:
                            conn.close()
