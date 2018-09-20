"""
This file defines our custom Sanic app class
"""
import logging

from sanic import Sanic

from elasticsearch import Elasticsearch


class SanicElasticsearch(Sanic):
    def __init__(self, *args, **kwargs):
        from server.request.ons_request import ONSRequest
        from server.elasticsearch_client_service import ElasticsearchClientService
        # Initialise APP with custom ONSRequest class
        super(SanicElasticsearch, self).__init__(*args, request_class=ONSRequest, **kwargs)

        # Attach an Elasticsearh client
        self.elasticsearch = None

        @self.listener("after_server_start")
        async def init(app: SanicElasticsearch, loop):
            """
            Initialise the ES client after server start (when the ioloop exists)
            :param app:
            :param loop:
            :return:
            """
            app.elasticsearch: ElasticsearchClientService = ElasticsearchClientService(app, loop)

            elasticsearch_log_data = {
                "data": {
                    "elasticsearch.host": self.elasticsearch.elasticsearch_host,
                    "elasticsearch.async": self.elasticsearch.elasticsearch_async_enabled,
                    "elasticsearch.timeout": self.elasticsearch.elasticsearch_timeout
                }
            }

            logging.info("Initialised Elasticsearch client", extra=elasticsearch_log_data)

        @self.listener("after_server_stop")
        async def shutdown(app: SanicElasticsearch, loop):
            """
            Trigger clean shutdown of ES client
            :param app:
            :param loop:
            :return:
            """
            await app.elasticsearch.shutdown()

    @property
    def elasticsearch_client(self) -> Elasticsearch:
        """
        Return the correct client instance
        :return:
        """
        return self.elasticsearch.client
