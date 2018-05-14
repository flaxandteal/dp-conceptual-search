from sanic.request import Request
from sanic.handlers import ErrorHandler
from sanic.exceptions import SanicException

from pythonjsonlogger import jsonlogger
from datetime import datetime


class CustomHandler(ErrorHandler):

    def default(self, request, exception):
        # Here, we have access to the exception object
        # and can do anything with it (log, send to external service, etc)

        # Some exceptions are trivial and built into Sanic (404s, etc)
        if not isinstance(exception, SanicException):
            print(exception)

        # Then, we must finish handling the exception by returning
        # our response to the client
        # For this we can just call the super class' default handler
        return super().default(request, exception)


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(
            CustomJsonFormatter,
            self).add_fields(
            log_record,
            record,
            message_dict)
        if not log_record.get('timestamp'):
            # this doesn't use record.created, so it is slightly off
            now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            log_record['timestamp'] = now
        if log_record.get('level'):
            log_record['level'] = "[%s]" % log_record['level'].upper()
        else:
            log_record['level'] = "[%s]" % record.levelname


def get_elasticsearch_client(do_async=True, **kwargs):
    """
    Initialises an Elasticsearch client. Supports asynchronous calls (must supply
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


def create_app(testing=False):
    from sanic import Sanic
    from sanic.response import json
    from server.search.routes import search_blueprint

    import asyncio
    import uvloop

    from.log_config import default_log_config

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    # Initialise app
    app = Sanic(log_config=default_log_config)
    app.config["TESTING"] = testing

    # Register blueprint(s)
    app.blueprint(search_blueprint)

    # Setup custom error handler
    handler = CustomHandler()
    app.error_handler = handler

    @app.route("/healthcheck")
    async def health_check(request):
        import inspect
        es_health = request.app.es_client.cluster.health()
        if inspect.isawaitable(es_health):
            es_health = await es_health
        return json(es_health, 200)

    # Initialise a single (Async) Elasticsearch client for each worker after
    # app start (in order to share event loop)
    @app.listener("after_server_start")
    async def prepare_dbs(current_app, loop):
        import os
        from sanic.log import logger
        assert isinstance(current_app, Sanic)

        if current_app.config["TESTING"] is False:
            do_async = os.getenv(
                "ELASTIC_SEARCH_ASYNC_ENABLED",
                "true").lower() == "true"
            current_app.es_client = get_elasticsearch_client(
                do_async=do_async, loop=loop)
            current_app.es_is_async = do_async
        else:
            from tests.server.search.test_search_client import FakeElasticsearch
            logger.warn("Test client active, using FakeElasticsearch client")
            current_app.es_client = FakeElasticsearch()

    @app.listener("after_server_stop")
    async def shutdown_dbs(current_app, loop):
        if hasattr(
            current_app,
            "es_client") and hasattr(
                current_app.es_client,
                "transport"):
            if hasattr(
                current_app.es_client.transport,
                "connection_pool") and hasattr(
                    current_app.es_client.transport.connection_pool,
                    "connections"):
                # Manually shutdown ES connections (await if async)
                for conn in current_app.es_client.transport.connection_pool.connections:
                    if current_app.es_is_async:
                        await conn.close()
                    else:
                        conn.close()

    @app.middleware('request')
    async def hash_ga_ids(request):
        """
        Intercepts all requests and hashes Google Analytics IDs
        :param request:
        :return:
        """
        from .anonymize import hash_value
        assert isinstance(request, Request)

        for key in ["_ga", "_gid"]:
            if key in request.cookies:
                value = request.cookies.pop(key)
                request.cookies[key] = hash_value(value)

    return app
