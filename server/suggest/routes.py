from sanic import Blueprint
from sanic.request import Request
from sanic.response import json, HTTPResponse

suggest_blueprint = Blueprint('suggest', url_prefix='/suggest')


@suggest_blueprint.route('/spelling', methods=["GET"])
def spell_checker(request: Request) -> HTTPResponse:
    """
    Spell checks each token in query
    :param request:
    :return:
    """
    from server.requests import get_request_param
    from server.word_embedding.sanic_word2vec import Models

    from core.suggest.spell_checker import SpellChecker

    query = get_request_param(request, "q", True)

    # Load the spell checker model
    model = SpellChecker(Models.ONS)

    # Generate the tokens
    tokens = query.split()

    # Get the result
    result = model.correct_terms(tokens)

    # Return the json response
    return json(result)
