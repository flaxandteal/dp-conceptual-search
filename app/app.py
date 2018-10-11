"""
Code for creating HTTP api app
"""
import asyncio
import uvloop

from config import CONFIG

from sanic.log import logger

from app.logging.log_config import log_config
from app.sanic_search import SanicSearch
from app.exceptions.error_handlers import ErrorHandlers

# Import blueprints
from api.search.routes import search_blueprint
from api.suggest.routes import suggest_blueprint
from api.healthcheck.routes import healthcheck_blueprint


def create_app() -> SanicSearch:
    """
    Creates the Sanic APP and registers all blueprints
    :return:
    """
    # First, set the ioloop event policy to use uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    # Now initialise the APP config, logger and ONSRequest handler
    app = SanicSearch(log_config=log_config)

    logger.info("Using config:", extra={"config": CONFIG.to_dict()})
    app.config.from_pyfile('config/config_sanic.py')

    # Register blueprints
    app.blueprint(search_blueprint)
    app.blueprint(suggest_blueprint)
    app.blueprint(healthcheck_blueprint)

    # Register error handlers
    ErrorHandlers.register(app)

    return app
