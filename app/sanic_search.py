"""
This file defines our custom Sanic app class
"""
from sanic.log import logger

from sanic import Sanic

from api.request.ons_request import ONSRequest
from app.elasticsearch_client_service import ElasticsearchClientService


class SanicSearch(Sanic):
    def __init__(self, *args, **kwargs):
        # Initialise APP with custom ONSRequest class
        super(SanicSearch, self).__init__(*args, request_class=ONSRequest, **kwargs)

        # Attach an Elasticsearh client
        self._elasticsearch = None

        @self.listener("after_server_start")
        async def init(app: SanicSearch, loop):
            """
            Initialise the ES client after api start (when the ioloop exists)
            :param app:
            :param loop:
            :return:
            """
            app._elasticsearch: ElasticsearchClientService = ElasticsearchClientService(app, loop)

            elasticsearch_log_data = {
                "data": {
                    "elasticsearch.host": self.elasticsearch.elasticsearch_host,
                    "elasticsearch.async": self.elasticsearch.elasticsearch_async_enabled,
                    "elasticsearch.timeout": self.elasticsearch.elasticsearch_timeout
                }
            }

            logger.info("Initialised Elasticsearch client", extra=elasticsearch_log_data)

        @self.listener("after_server_stop")
        async def shutdown(app: SanicSearch, loop):
            """
            Trigger clean shutdown of ES client
            :param app:
            :param loop:
            :return:
            """
            await app.elasticsearch.shutdown()

    @property
    def elasticsearch(self) -> ElasticsearchClientService:
        return self._elasticsearch
