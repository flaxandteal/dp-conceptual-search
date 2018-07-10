from sanic import Blueprint
from sanic.request import Request
from sanic.response import json, HTTPResponse
from sanic.exceptions import InvalidUsage

from core.recommend.engine import RecommendationEngine

from typing import Callable

recommend_blueprint = Blueprint('recommend', url_prefix='/recommend')


def get_recommendation_engine(request: Request) -> RecommendationEngine:
    """

    :param request:
    :return:
    """
    from core.users.user import User
    from server.users import get_user_id, get_session_id

    user_id = get_user_id(request)
    session_id = get_session_id(request)

    if user_id is not None and session_id is not None:
        engine = RecommendationEngine(user_id, session_id)

        return engine
    raise InvalidUsage("Must supply '%s' cookie" % User.user_id_key)


async def update_by_term(request: Request, term: str, update_func: Callable) -> HTTPResponse:
    """
    Performs a generic reinforcement of the users vector, using the given term
    :param request:
    :param term:
    :param update_func:
    :return:
    """
    engine = get_recommendation_engine(request)
    session = await engine.update_session_vector_by_term(term, update_func)

    return json(session.to_json(), 200)


@recommend_blueprint.route('/update/page/', methods=['POST'])
@recommend_blueprint.route('/update/page/<path:path>', methods=['POST'])
async def update_by_document(request: Request, path: str):
    """
    Performs a generic reinforcement of the users vector, using the given term
    :param request:
    :param path:
    :return:
    """
    import numpy as np

    from server.requests import get_form_param
    from core.users.distance_utils import default_move_session_vector, negative_move_session_vector

    from server.search.routes import find_document_by_uri
    from core.word_embedding.utils import decode_float_list

    from ons.search.fields import embedding_vector

    from sanic.exceptions import NotFound

    # Query for a page with this uri
    response: dict = await find_document_by_uri(request, path)

    # Document exists - get the embedding_vector
    documents: list = response.get('results', [])

    if len(documents) > 0:
        document = documents[0]

        doc_vector = document.get(embedding_vector.name)
        if doc_vector is not None and isinstance(doc_vector, str):
            # Decode the vector
            decoded_doc_vector = np.array(decode_float_list(doc_vector))

            # Update the user

            engine = get_recommendation_engine(request)
            sentiment: str = get_form_param(
                request, "sentiment", False, default="positive")

            if sentiment.lower() == "positive":
                session = await engine.update_session_vector(decoded_doc_vector, default_move_session_vector)
            elif sentiment.lower() == "negative":
                session = await engine.update_session_vector(decoded_doc_vector, negative_move_session_vector)
            else:
                raise InvalidUsage("Unknown sentiment: '%s'" % sentiment)

            return json(session.to_json(), 200)
    raise NotFound("Unable to find page with uri '%s'" % path)


@recommend_blueprint.route('/update/positive/<term>', methods=['POST'])
async def positive_update(request: Request, term: str):
    """
    Performs a positive reinforcement of the users vector, using the given term
    :param request:
    :param term:
    :return:
    """
    from core.users.distance_utils import default_move_session_vector
    return await update_by_term(request, term, default_move_session_vector)


@recommend_blueprint.route('/update/negative/<term>', methods=['POST'])
async def negative_update(request: Request, term: str):
    """
    Performs a negative reinforcement of the users vector, using the given term
    :param request:
    :param term:
    :return:
    """
    from core.users.distance_utils import negative_move_session_vector
    return await update_by_term(request, term, negative_move_session_vector)


@recommend_blueprint.route('/similarity/<term>', methods=['GET'])
async def similarity(request: Request, term: str):
    """
    Measure how likely the current user is to be interested in the specified term.
    :param request:
    :param term:
    :return: 200 OK with similarity score if user exists. 404 NOT_FOUND if the user doesn't exist.
    """
    from core.users.user import User
    from server.users import get_user_id

    user_id = get_user_id(request)
    if user_id is not None:
        return await similarity(request, user_id, term)
    raise InvalidUsage("Must supply '%s' cookie" % User.user_id_key)


@recommend_blueprint.route('/similarity/<user_id>/<term>', methods=['GET'])
async def similarity(request: Request, user_id: str, term: str):
    """
    Measure how likely this user is to be interested in the specified term
    :param request:
    :param user_id:
    :param term:
    :return: 200 OK with similarity score if user exists. 404 NOT_FOUND if the user doesn't exist.
    """
    from server.users import get_user
    from sanic.response import json

    user = await get_user(user_id)

    if user is not None:
        from server.word_embedding.sanic_supervised_models import load_model

        from core.word_embedding.models.supervised import SupervisedModels
        from core.word_embedding.utils import cosine_sim

        model = load_model(SupervisedModels.ONS)

        term_vector = model.get_sentence_vector(term)
        user_vector = await user.get_user_vector()

        sim = cosine_sim(user_vector, term_vector)

        response = {
            'user_id': user_id,
            'term': term,
            'similarity': sim
        }

        return json(response, 200)
    return json("User '%s' not found" % user_id, 404)

@recommend_blueprint.route('/content/', methods=['GET', 'POST'])
@recommend_blueprint.route('/content/<path:path>', methods=['GET', 'POST'])
async def content_query(request: Request, path: str):
    """
    Request for recommended content.
    If user_id cookie is present, combine into function score.
    TODO - refactor and simplify
    :param request:
    :param path:
    :return:
    """
    from core.users.user import User

    from ons.search.indicies import Index
    from ons.search.response import ONSResponse
    from ons.search.conceptual.search_engine import ConceptualSearchEngine

    from server.requests import get_form_param

    # Execute the query
    app = request.app
    es_client = app.es_client
    s = ConceptualSearchEngine(using=es_client, index=Index.ONS.value)

    # Check if user_id cookie exists
    user_id = request.cookies.get(User.user_id_key, None)

    s: ConceptualSearchEngine = await s.recommend_query(path, user_id=user_id)

    # Paginate
    page_number = int(get_form_param(request, "page", False, 1))
    page_size = int(get_form_param(request, "size", False, 1))
    s: ConceptualSearchEngine = s.paginate(page_number, page_size)

    # Execute
    response: ONSResponse = await s.execute()
    result = response.response_to_json(page_number, page_size)

    return json(result, 200)
