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


async def get_elastic_search_client(
        search_url: str,
        search_timeout: int,
        loop=None,
        async_client: bool=False):
    """
    Initialises an Elasticsearch client. Supports asynchronous calls (must supply Sanic event loop)
    :param loop:
    :param search_url:
    :param search_timeout:
    :param loop:
    :param async_client:
    :return:
    """
    from sanic.log import logger
    from inspect import isawaitable

    if async_client:
        from elasticsearch_async import AsyncElasticsearch

        logger.info(
            "Initialising async Elasticsearch client URL:%s timeout:%d" %
            (search_url, search_timeout))

        if loop is None:
            import sys
            logger.error(
                "AsyncElasticsearch client requires the Sanic event loop!")
            sys.exit(1)

        client = AsyncElasticsearch(
            search_url, loop=loop, timeout=search_timeout)
    else:
        from elasticsearch_async import Elasticsearch

        logger.info(
            "Initialising Elasticsearch client URL:%s timeout:%d" %
            (search_url, search_timeout))

        client = Elasticsearch(search_url, timeout=search_timeout)

    try:
        # Check cluster health
        info = client.cluster.health()
        if isawaitable(info):
            info = await info
    except Exception as e:
        import sys
        from sanic.log import logger
        message = "Unable to make initial connection to Elasticsearch on url '%s': %s" % (
            search_url, e)
        logger.error(message)
        sys.exit(1)

    if "status" not in info or info["status"] == "red":
        import sys
        from sanic.log import logger
        message = "Elasticsearch cluster status unavailable or red: '%s'" % (
            info["status"] if "status" in info else "unavailable")
        logger.error(message)
        sys.exit(1)

    return client


class SanicElasticsearch(SanicExtension):
    """
    Class to handle the init/tear down of ES clients for Sanic
    """

    def init_app(self, app: Sanic, **kwargs) -> None:
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

                _app.es_client = await get_elastic_search_client(
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
