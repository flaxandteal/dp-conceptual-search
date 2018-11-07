"""
Code for creating HTTP api app
"""
import asyncio
import uvloop
import logging

from dp4py_sanic.app.exceptions.error_handlers import ErrorHandlers

from dp_conceptual_search.app.search_app import SearchApp
from dp_conceptual_search.config import CONFIG, SANIC_CONFIG

# Import blueprints
from dp_conceptual_search.api.search.routes import search_blueprint
from dp_conceptual_search.api.spellcheck.routes import spell_check_blueprint
from dp_conceptual_search.api.healthcheck.routes import healthcheck_blueprint


def create_app() -> SearchApp:
    """
    Creates the Sanic APP and registers all blueprints
    :return:
    """
    # First, set the ioloop event policy to use uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    # Set elasticsearch log level
    logging.getLogger('elasticsearch').setLevel(CONFIG.ELASTIC_SEARCH.elasticsearch_log_level)

    # Now initialise the APP config, logger and ONSRequest handler
    app = SearchApp(CONFIG.APP.title)

    logging.info("Using config:", extra={"config": CONFIG.to_dict()})

    # Register blueprints
    app.blueprint(search_blueprint)
    app.blueprint(spell_check_blueprint)
    app.blueprint(healthcheck_blueprint)

    # Register error handlers
    ErrorHandlers.register(app)

    return app
