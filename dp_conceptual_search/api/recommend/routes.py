"""
Defines the recommendation routes
"""
from sanic.blueprints import Blueprint

from dp4py_logging.time import timeit
from dp4py_sanic.api.response.json_response import json

from dp_conceptual_search.log import logger
from dp_conceptual_search.api.request import ONSRequest
from dp_conceptual_search.app.search_app import SearchApp

from dp_conceptual_search.ons.search import SortField
from dp_conceptual_search.ons.search.index import Index
from dp_conceptual_search.ons.search.response.client.ons_response import ONSResponse
from dp_conceptual_search.ons.recommend.client.recommend_search_engine import RecommendationSearchEngine


recommend_blueprint = Blueprint('recommend', url_prefix='/recommend')


@recommend_blueprint.route('/similar/', methods=['POST'])
@timeit
async def recommend_content_by_uri(request: ONSRequest):
    """
    Returns content similar to the input uri
    :param request:
    :param path:
    :return:
    """
    # Get unsupervised model
    app: SearchApp = request.app

    # Init engine
    s: RecommendationSearchEngine = RecommendationSearchEngine(using=app.elasticsearch.client, index=Index.ONS.value)

    # Get uri from POST params
    uri = request.get_uri()

    # Get pagination params
    page = request.get_current_page()
    page_size = request.get_page_size()
    sort_by: SortField = request.get_sort_by()

    # Get num_labels param
    num_labels: int = request.get_num_labels()

    # Build the query
    s: RecommendationSearchEngine = await s.similar_by_uri_query(uri, num_labels,
                                                                 page, page_size,
                                                                 sort_by=sort_by,
                                                                 highlight=True)

    # Execute
    try:
        response: ONSResponse = await s.execute()

        # Return JSON response
        response = response.to_content_query_search_result(page, page_size, sort_by).to_dict()
        return json(request, response, 200)
    except Exception as e:
        logger.error(request.request_id, "Caught exception executing 'similar_to_uri' query", exc_info=e)
        return json(request, "Caught exception executing 'similar_to_uri' query", 500)
