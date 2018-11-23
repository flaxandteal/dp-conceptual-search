"""
Class for dp-fasttext healthchecks
"""
from .healthcheck import HealthCheck

from typing import Tuple

from dp_fasttext.client import Client

from dp_conceptual_search.log import logger
from dp_conceptual_search.api.request import ONSRequest
from dp_conceptual_search.ons.conceptual.client import FastTextClientService


class DpFastTextHealthCheck(HealthCheck):

    AVAILABLE = "available"
    UNREACHABLE = "unreachable"
    UNAVAILABLE = "unavailable"

    async def healthcheck(self, request: ONSRequest) -> Tuple[str, int]:
        """
        Checks if dp-fasttext is healthy
        :param request:
        :return:
        """
        client: Client
        async with FastTextClientService.get_fasttext_client() as client:
            headers = {
                Client.REQUEST_ID_HEADER: request.request_id
            }

            try:
                response, headers = await client.healthcheck(headers=headers)

                if response is not None and \
                    Client.REQUEST_ID_HEADER in headers and headers[Client.REQUEST_ID_HEADER] == request.request_id:
                    return self.AVAILABLE, 200
            except Exception as e:
                logger.error(request.request_id, "Caught exception checking health of dp-fasttext", exc_info=e)
                return self.UNREACHABLE, 500

            return self.UNAVAILABLE, 500
