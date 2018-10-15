"""
This file contains all routes for the /suggest API
"""
from sanic import Blueprint

from api.response import json
from api.request import ONSRequest
from ml.spelling.spell_checker import SpellChecker

suggest_blueprint = Blueprint('suggest', url_prefix='/suggest')


@suggest_blueprint.route('/spelling', methods=['GET'], strict_slashes=True)
async def spell_check(request: ONSRequest):
    """
    API for spell checking
    :param request:
    :return:
    """
    search_term = request.get_search_term()

    # Get spell checker
    spell_checker: SpellChecker = request.get_app().spell_checker

    # Generate the tokens
    tokens = search_term.split()

    # Get the result
    result = spell_checker.correct_spelling(tokens)

    # Return the json response
    return json(request, result, 200)
