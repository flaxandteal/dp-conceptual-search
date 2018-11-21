"""
Defines all healthcheck methods
Should all take arguments (request: ONSRequest)
"""
from .healthcheck import HealthCheck

from typing import Tuple
from inspect import isawaitable

from elasticsearch import Elasticsearch

from dp_conceptual_search.log import logger
from dp_conceptual_search.config.config import SEARCH_CONFIG

from dp_conceptual_search.api.request import ONSRequest
from dp_conceptual_search.app.search_app import SearchApp


class ElasticsearchHealthCheck(HealthCheck):

    def __init__(self):
        self.indices = "{ons},{departments}".format(ons=SEARCH_CONFIG.search_index,
                                                    departments=SEARCH_CONFIG.departments_search_index)

    async def healthcheck(self, request: ONSRequest) -> Tuple[str, int]:
        """
        Checks if Elasticsearch is healthy or not
        :param request:
        :return:
        """
        # Ping elasticsearch to get cluster health
        app: SearchApp = request.app

        # Init the HTTP client
        client: Elasticsearch = app.elasticsearch.client

        # Send the request
        try:
            health = client.cluster.health()
            if isawaitable(health):
                health = await health

            if 'status' not in health:
                logger.error(request.request_id, "Malformed health response", extra={
                    "data": health
                })
                return "malformed response", 500
            elif health['status'] not in ['yellow', 'green']:
                logger.error(request.request_id, "Elasticsearch cluster is unhealthy", extra={
                    "data": health
                })
                return "cluster unhealthy [status={status}]".format(status=health['status']), 500

            # Check indices exist
            indices_exist = client.indices.exists(self.indices)
            if isawaitable(indices_exist):
                indices_exist = await indices_exist

            if indices_exist:
                return "available", 200
            else:
                logger.error(request.request_id, "Search indicies do not exist", extra={
                    "Elasticsearch indices_checked": self.indices
                })
                return "indices unavailable [indices={indices}]".format(indices=self.indices), 500
        except Exception as e:
            logger.error(request.request_id, "Unable to get Elasticsearch cluster health", exc_info=e)
            return "unreachable", 500
