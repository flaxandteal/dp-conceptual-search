"""
Code for creating HTTP server app
"""
from sanic import Sanic


def init_app() -> Sanic:
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
    app = Sanic(log_config=default_log_config, request_class=ONSRequest)

    logger.info("Using config '%s'" % config_name)
    app.config.from_pyfile('config_%s.py' % config_name)

    return app


def register_blueprints(app: Sanic):
    """
    Registers blueprints against a Sanic APP
    :param app:
    :return:
    """


def create_app() -> Sanic:
    """
    Creates the Sanic APP and registers all blueprints
    :return:
    """
    app: Sanic = init_app()
    register_blueprints(app)

    return app
