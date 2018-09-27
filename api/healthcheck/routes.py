"""
Healthcheck API
"""
from sanic import Blueprint
from inspect import isawaitable

from elasticsearch import Elasticsearch

from app.sanic_search import SanicSearch

from api.log import logger
from api.response import json
from api.request.ons_request import ONSRequest

healthcheck_blueprint = Blueprint('healthcheck', url_prefix='/healthcheck')


@healthcheck_blueprint.route('/', methods=['GET'])
async def health_check(request: ONSRequest):
    """
    API to check health of the app (i.e connection status to Elasticsearch)
    :param request:
    :return:
    """
    # Ping elasticsearch to get cluster health
    app: SanicSearch = request.get_app()

    client: Elasticsearch = app.elasticsearch.client

    # Send the request
    try:
        health = client.cluster.health()
        if isawaitable(health):
            health = await health
        return json(request, health, 200)
    except Exception as e:
        logger.error(request, "Unable to get Elasticsearch cluster health", exc_info=e)
        body = {
            "elasticsearch": "unavaialable"
        }
        return json(request, body, 500)
