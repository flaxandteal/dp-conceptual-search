from sanic import Sanic


def get_elastic_search_client(**kwargs):
    """
    Initialises an Elasticsearch client. Supports asynchronous calls (must supply Sanic event loop)
    :param async:
    :param kwargs:
    :return:
    """
    import os
    from sanic.log import logger

    search_url = os.environ.get(
        'ELASTIC_SEARCH_SERVER',
        'http://localhost:9200')
    search_timeout = int(os.environ.get('ELASTIC_SEARCH_TIMEOUT', 1000))

    do_async = os.getenv(
        "ELASTIC_SEARCH_ASYNC_ENABLED",
        "true").lower() == "true"

    if do_async:
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


class SanicElasticsearch(object):
    """
    Class to handle the init/tear down of ES clients for Sanic
    """

    def __init__(self, app: Sanic=None):
        self.app = app

        if app:
            self.init_app(app=app)

    def init_app(self, app: Sanic):
        """
        Registers init/shutdown hooks for Elasticsearch
        :param app:
        :return:
        """
        self.app = app

        @app.listener("after_server_start")
        async def elastic_search_configure(_app: Sanic, loop):
            if _app.config.get("TESTING", False) is False:
                _app.es_client = get_elastic_search_client(loop=loop)
            else:
                from tests.server.search.test_search_client import FakeElasticsearch
                from sanic.log import logger

                logger.warn(
                    "Test client active, using FakeElasticsearch client")
                _app.es_client = FakeElasticsearch()

        @app.listener("after_server_stop")
        async def shutdown_dbs(_app, loop):
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
