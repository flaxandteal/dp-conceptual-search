"""
Healthcheck API
"""
from .services import Service
from .response import HealthCheckResponse

from sanic import Blueprint

from dp_conceptual_search.log import logger
from dp_conceptual_search.api.response import json
from dp_conceptual_search.api.request.ons_request import ONSRequest

healthcheck_blueprint = Blueprint('healthcheck', url_prefix='/healthcheck')


@healthcheck_blueprint.route('/', methods=['GET'])
async def health_check(request: ONSRequest):
    """
    API to check health of the app (i.e connection status to Elasticsearch)
    :param request:
    :return:
    """
    # Init the response body
    response: HealthCheckResponse = HealthCheckResponse()

    service: Service
    for service in Service:
        health_check_fn = service.value
        message, code = await health_check_fn(request)

        response.set_response_for_service(service, message, code)

    body = response.to_dict()

    logger.info(request.request_id, "Health check response", extra={
        "body": body
    })
    if not response.is_healthy:
        return json(request, body, 500)

    return json(request, body, 200)
