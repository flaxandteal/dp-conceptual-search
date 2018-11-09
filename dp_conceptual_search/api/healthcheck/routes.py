"""
Healthcheck API
"""
from sanic import Blueprint
from inspect import isawaitable

from elasticsearch import Elasticsearch

from dp_conceptual_search.app.search_app import SearchApp

from dp_conceptual_search.api.log import logger
from dp_conceptual_search.api.response import json
from dp_conceptual_search.api.request.ons_request import ONSRequest
from dp_conceptual_search.config.config import SEARCH_CONFIG

healthcheck_blueprint = Blueprint('healthcheck', url_prefix='/healthcheck')


@healthcheck_blueprint.route('/', methods=['GET'])
async def health_check(request: ONSRequest):
    """
    API to check health of the app (i.e connection status to Elasticsearch)
    :param request:
    :return:
    """
    # Ping elasticsearch to get cluster health
    app: SearchApp = request.app

    client: Elasticsearch = app.elasticsearch.client

    # Send the request
    try:
        health = client.cluster.health()
        if isawaitable(health):
            health = await health

        code = 200 if 'status' in health and health['status'] in ['yellow', 'green'] else 500

        if code != 200:
            logger.error(request.request_id, "Healthcheck results in non-200 response", extra={"health": health})

        # Check indices exist
        indices = "{ons},{departments}".format(ons=SEARCH_CONFIG.search_index,
                                               departments=SEARCH_CONFIG.departments_search_index)
        indicies_exist = client.indices.exists(indices)
        if isawaitable(indicies_exist):
            indicies_exist = await indicies_exist

        if indicies_exist:
            return json(request, health, code)
        else:
            logger.error(request.request_id, "Search indicies do not exist", extra={
                "Elasticsearch indices_checked": indices
            })
            body = {"indices not found": indices}
            return json(request, body, 500)
    except Exception as e:
        logger.error(request.request_id, "Unable to get Elasticsearch cluster health", exc_info=e)
        body = {
            "elasticsearch": "unavailable"
        }
        return json(request, body, 500)
