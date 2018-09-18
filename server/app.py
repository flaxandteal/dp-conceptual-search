"""
Code for creating HTTP server app
"""
from server.sanic_elasticsearch import SanicElasticsearch


def init_app() -> SanicElasticsearch:
    """
    Initialises the default state for the Sanic APP
    :return:
    """
    import os
    import asyncio
    import uvloop

    from sanic.log import logger

    from server.request import ONSRequest
    from server.log_config import default_log_config

    # First, set the ioloop event policy to use uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    # Now initialise the APP config, logger and ONSRequest handler
    config_name = os.environ.get('SEARCH_CONFIG', 'development')
    app = SanicElasticsearch(log_config=default_log_config, request_class=ONSRequest)

    logger.info("Using config '%s'" % config_name)
    app.config.from_pyfile('config_%s.py' % config_name)

    return app


def register_blueprints(app: SanicElasticsearch):
    """
    Registers blueprints against a Sanic APP
    :param app:
    :return:
    """
    from server.search.routes import search_blueprint

    app.blueprint(search_blueprint)


def create_app() -> SanicElasticsearch:
    """
    Creates the Sanic APP and registers all blueprints
    :return:
    """
    app: SanicElasticsearch = init_app()
    register_blueprints(app)

    return app
