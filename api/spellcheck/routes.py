"""
This file contains all routes for the /spellcheck API
"""
from sanic import Blueprint

from api.response import json
from api.request import ONSRequest
from api.log import logger

from app.search_app import SearchApp

from ml.spelling.spell_checker import SpellChecker

spell_check_blueprint = Blueprint('spellcheck', url_prefix='/spellcheck')


@spell_check_blueprint.route('/', methods=['GET'], strict_slashes=False)
async def spell_check(request: ONSRequest):
    """
    API for spell checking
    :param request:
    :return:
    """
    search_term = request.get_search_term()

    # Get spell checker
    app: SearchApp = request.app
    spell_checker: SpellChecker = app.spell_checker

    # Generate the tokens
    tokens = search_term.split()
    if len(tokens) > 0:
        # Get the result
        result = spell_checker.correct_spelling(tokens)

        # Return the json response
        return json(request, result, 200)

    # No input tokens - raise a 400 BAD_REQUEST
    message = "Found no input tokens in query: %s" % search_term
    logger.error(request.request_id, message)
    return json(request, message, 400)
