from sanic import Sanic
from sanic.request import Request

from sanic_motor import BaseModel


def init_default_app() -> Sanic:
    import os
    import asyncio
    import uvloop

    from server.log_config import default_log_config
    from server.error_handlers import CustomHandler
    from server.sanic_es import SanicElasticsearch

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    config_name = os.environ.get('SEARCH_CONFIG', 'development')

    # Initialise app
    app = Sanic(log_config=default_log_config)
    app.config.from_pyfile('config_%s.py' % config_name)

    if app.config.get("CONCEPTUAL_SEARCH_ENABLED", False):
        # Trigger loading of models - TODO improve this
        from .word_embedding import supervised_models
        supervised_models.init()

        # Initialse MongoEngine
        BaseModel.init_app(app)

    if app.config.get("ENABLE_PROMETHEUS_METRICS", False):
        from sanic_prometheus import monitor
        # adds /metrics endpoint to your Sanic server
        monitor(app).expose_endpoint()

    # Setup custom error handler
    app.error_handler = CustomHandler()

    # Initialise Elasticsearch client
    SanicElasticsearch(app)

    # Register blueprints
    register_blueprints(app)

    return app


def register_blueprints(app: Sanic) -> None:
    # Register blueprint(s)
    from server.search.routes import search_blueprint
    from server.healthcheck.routes import health_check_blueprint

    app.blueprint(search_blueprint)
    app.blueprint(health_check_blueprint)

    conceptual_search_enabled = app.config.get(
        "CONCEPTUAL_SEARCH_ENABLED", False)

    if conceptual_search_enabled:
        from server.users.routes import user_blueprint
        from server.users.routes_sessions import sessions_blueprint
        from server.search.conceptual_search.routes import conceptual_search_blueprint

        app.blueprint(user_blueprint)
        app.blueprint(sessions_blueprint)
        app.blueprint(conceptual_search_blueprint)


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
        from server.anonymize import hash_value
        from server.users.user import User
        from server.users.session import Session

        for key in ["_ga", "_gid"]:
            if key in request.cookies:
                value = request.cookies.pop(key)
                request.cookies[key] = hash_value(value)

        conceptual_search_enabled = app.config.get(
            "CONCEPTUAL_SEARCH_ENABLED", False)

        if conceptual_search_enabled:
            # If user/session doesn't exist, create them
            if '_ga' in request.cookies:
                user_id = request.cookies.get('_ga')
                user = await User.find_by_user_id(user_id)

                if user is None:
                    user = User(user_id)
                    await user.write()
                    user = await User.find_by_user_id(user_id)

                if '_gid' in request.cookies and user is not None:
                    session_id = request.cookies.get('_gid')
                    session = await Session.find_by_session_id(session_id)

                    if session is None:
                        session = Session(user.id, session_id)
                        await session.write()

    return app
