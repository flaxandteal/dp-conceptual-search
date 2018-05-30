from sanic import Sanic
from sanic.request import Request


def init_default_app() -> Sanic:
    import os
    import asyncio
    import uvloop

    from .log_config import default_log_config
    from .error_handlers import CustomHandler
    from .sanic_es import SanicElasticsearch

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    config_name = os.environ.get('SEARCH_CONFIG', 'development')

    # Initialise app
    app = Sanic(log_config=default_log_config)
    app.config.from_pyfile('config_%s.py' % config_name)

    if app.config.get("CONCEPTUAL_SEARCH_ENABLED", False):
        # Trigger loading of models - TODO improve this
        from .word_embedding import supervised_models
        supervised_models.init()

    if app.config.get("ENABLE_PROMETHEUS_METRICS", False):
        from sanic_prometheus import monitor
        # adds /metrics endpoint to your Sanic server
        monitor(app).expose_endpoint()

    # Setup custom error handler
    app.error_handler = CustomHandler()

    # Initialise Elasticsearch client
    SanicElasticsearch(app)

    register_blueprints(app)
    return app


def register_blueprints(app: Sanic) -> None:
    # Register blueprint(s)
    from server.search.routes import search_blueprint
    from server.healthcheck.routes import health_check_blueprint
    app.blueprint(search_blueprint)
    app.blueprint(health_check_blueprint)


def create_app() -> Sanic:
    app = init_default_app()

    # Setup middleware

    @app.middleware('request')
    async def hash_ga_ids(request: Request):
        """
        Intercepts all requests and hashes Google Analytics IDs
        :param request:
        :return:
        """
        from .anonymize import hash_value

        for key in ["_ga", "_gid"]:
            if key in request.cookies:
                value = request.cookies.pop(key)
                request.cookies[key] = hash_value(value)

    return app
