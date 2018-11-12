"""
Healthcheck API
"""
from enum import Enum
from sanic import Blueprint
from functools import partial
from inspect import isawaitable

from elasticsearch import Elasticsearch

from dp4py_sanic.api.response import json

from dp_conceptual_search.log import logger
from dp_conceptual_search.app.search_app import SearchApp
from dp_conceptual_search.api.request.ons_request import ONSRequest
from dp_conceptual_search.config.config import SEARCH_CONFIG

healthcheck_blueprint = Blueprint('healthcheck', url_prefix='/healthcheck')


async def elasticsearch_is_healthy(request: ONSRequest) -> bool:
    """
    Checks if Elasticsearch is healthy or not
    :param request:
    :param client:
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

        if not 'status' in health or health['status'] not in ['yellow', 'green']:
            logger.error("Elasticsearch cluster is unhealthy", extra={
                "data": health
            })
            return False

        # Check indices exist
        indices = "{ons},{departments}".format(ons=SEARCH_CONFIG.search_index,
                                               departments=SEARCH_CONFIG.departments_search_index)
        indicies_exist = client.indices.exists(indices)
        if isawaitable(indicies_exist):
            indicies_exist = await indicies_exist

        if indicies_exist:
            return True
        else:
            logger.error(request.request_id, "Search indicies do not exist", extra={
                "Elasticsearch indices_checked": indices
            })
            return False
    except Exception as e:
        logger.error(request.request_id, "Unable to get Elasticsearch cluster health", exc_info=e)
        return False


async def dp_fasttext_is_healthy(request: ONSRequest) -> bool:
    """
    Checks the health of dp-fasttext
    :param request:
    :return:
    """
    return True


class Services(Enum):
    ELASTICSEARCH = partial(elasticsearch_is_healthy)
    FASTTEXT = partial(dp_fasttext_is_healthy)


class HeathCheckResponse(object):

    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"

    def __init__(self):
        self.is_healthy = True
        self._services = {}

    async def evaluate(self, service: Services, request: ONSRequest):
        """
        Evaluate health of given service
        :param service:
        :param request:
        :return:
        """
        fn = service.value

        if await fn(request):
            self._set_available(service)
        else:
            self._set_unavailable(service)

    def _set_available(self, service: Services):
        """
        Mark a service as being available
        :param service:
        :return:
        """
        self._services[service.name.lower()] = self.AVAILABLE

    def _set_unavailable(self, service: Services):
        """
        Mark a service as being unavailable
        :param service:
        :return:
        """
        # Mark app as unhealthy
        self.is_healthy = False
        self._services[service.name.lower()] = self.UNAVAILABLE

    def to_dict(self):
        return self._services


@healthcheck_blueprint.route('/', methods=['GET'])
async def health_check(request: ONSRequest):
    """
    API to check health of the app (i.e connection status to Elasticsearch)
    :param request:
    :return:
    """
    # Init the response body
    response: HeathCheckResponse = HeathCheckResponse()

    service: Services
    for service in Services:
        await response.evaluate(service, request)

    body = response.to_dict()
    code = 200
    if not response.is_healthy:
        code = 500

    return json(request, body, code)
