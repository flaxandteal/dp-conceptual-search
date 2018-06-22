from sanic import Sanic
from sanic.request import Request
from sanic.log import logger

from sanic_motor import BaseModel


def init_default_app() -> Sanic:
    import os
    import asyncio
    import uvloop

    from server.log_config import default_log_config
    from server.error_handlers import CustomHandler
    from server.sanic_es import SanicElasticsearch

    from core.word_embedding.sanic_word2vec import SanicWord2Vec
    from core.word_embedding.sanic_supervised_models import SanicFastText

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    config_name = os.environ.get('SEARCH_CONFIG', 'development')

    # Initialise app
    app = Sanic(log_config=default_log_config)

    logger.info("Using config '%s'" % config_name)
    app.config.from_pyfile('config_%s.py' % config_name)

    if app.config.get("MONGO_ENABLED", False):
        # Init MongoEngine
        logger.info(
            "Initialising motor engine on uri '%s'" %
            app.config.get('MOTOR_URI'))
        BaseModel.init_app(app)

    if app.config.get("ENABLE_PROMETHEUS_METRICS", False):
        from sanic_prometheus import monitor
        # adds /metrics endpoint to your Sanic server
        monitor(app).expose_endpoint()

    # Setup custom error handler
    app.error_handler = CustomHandler()

    # Initialise Elasticsearch client
    SanicElasticsearch(app)

    # Initialise word2vec models
    SanicWord2Vec(app)

    # Initialise fastText models
    SanicFastText(app)

    return app


def register_blueprints(app: Sanic) -> None:
    # Register blueprint(s)
    from server.search.routes import search_blueprint
    from server.suggest.routes import suggest_blueprint
    from server.healthcheck.routes import health_check_blueprint
    from server.search.conceptual_search.routes import conceptual_search_blueprint

    app.blueprint(search_blueprint)
    app.blueprint(suggest_blueprint)
    app.blueprint(health_check_blueprint)
    app.blueprint(conceptual_search_blueprint)

    if app.config.get('MONGO_ENABLED', False):
        from server.users.routes import user_blueprint
        from server.users.routes_sessions import sessions_blueprint
        from server.recommend.routes import recommend_blueprint

        app.blueprint(user_blueprint)
        app.blueprint(sessions_blueprint)
        app.blueprint(recommend_blueprint)


def create_app() -> Sanic:
    app = init_default_app()

    # Register blueprints
    register_blueprints(app)

    # Setup middleware
    @app.middleware('request')
    async def hash_ga_ids(request: Request):
        """
        Intercepts all requests and hashes Google Analytics IDs
        :param request:
        :return:
        """
        from server.anonymize import hash_value

        for key in ["_ga", "_gid"]:
            if key in request.cookies:
                value = request.cookies.pop(key)
                request.cookies[key] = hash_value(value)

    if app.config.get("START_MONGO", False):
        @app.listener("before_server_start")
        async def start_mongod(_app: Sanic, loop):
            import os
            os.system("make mongo-start")

        @app.listener("after_server_stop")
        async def stop_mongod(_app: Sanic, loop):
            import os
            os.system("make mongo-stop")

    return app
