"""
Code for creating HTTP api app
"""
import os
import asyncio
import uvloop
import logging

from dp_conceptual_search.config import CONFIG, SANIC_CONFIG

from dp_conceptual_search.app.search_app import SearchApp
from dp_conceptual_search.app.exceptions.error_handlers import ErrorHandlers

# Import blueprints
from dp_conceptual_search.api.search.routes import search_blueprint
from dp_conceptual_search.api.search.conceptual.routes import conceptual_search_blueprint
from dp_conceptual_search.api.spellcheck.routes import spell_check_blueprint
from dp_conceptual_search.api.healthcheck.routes import healthcheck_blueprint


def create_app() -> SearchApp:
    """
    Creates the Sanic APP and registers all blueprints
    :return:
    """
    # First, set the ioloop event policy to use uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    # Set logging namespace
    if "LOGGING_NAMESPACE" not in os.environ:
        SANIC_CONFIG.LOGGING.namespace = CONFIG.APP.title

    # Now initialise the APP config, logger and ONSRequest handler
    app = SearchApp()

    logging.info("Using config:", extra={"config": CONFIG.to_dict()})

    # Register blueprints
    app.blueprint(search_blueprint)
    app.blueprint(spell_check_blueprint)
    app.blueprint(healthcheck_blueprint)

    # Enable conceptual search routes?
    if CONFIG.SEARCH.conceptual_search_enabled:
        app.blueprint(conceptual_search_blueprint)

    # Register error handlers
    ErrorHandlers.register(app)

    return app
