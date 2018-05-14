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


def create_app(testing=False):
    from sanic import Sanic
    from sanic.response import json
    from server.search.routes import search_blueprint

    import asyncio
    import uvloop

    from.log_config import default_log_config
    from .sanic_es import SanicElasticsearch

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    # Initialise app
    app = Sanic(log_config=default_log_config)
    app.config["TESTING"] = testing

    # Register blueprint(s)
    app.blueprint(search_blueprint)

    # Setup custom error handler
    handler = CustomHandler()
    app.error_handler = handler

    # Initialise Elasticsearch client
    SanicElasticsearch(app)

    # Define healthcheck API
    @app.route("/healthcheck")
    async def health_check(request):
        import inspect
        es_health = request.app.es_client.cluster.health()
        if inspect.isawaitable(es_health):
            es_health = await es_health
        return json(es_health, 200)

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
