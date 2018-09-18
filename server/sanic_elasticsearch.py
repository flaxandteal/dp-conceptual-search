"""
This file defines our custom Sanic app class
"""
from sanic import Sanic
from elasticsearch import Elasticsearch


class SanicElasticsearch(Sanic):
    def __init__(self, *args, **kwargs):
        from server.elasticsearch_client import ElasticsearchClientService
        super(SanicElasticsearch, self).__init__(*args, **kwargs)

        # Attach an Elasticsearh client
        self._es_client_service = None

        @self.listener("after_server_start")
        async def init(app: SanicElasticsearch, loop):
            """
            Initialise the ES client after server start (when the ioloop exists)
            :param app:
            :param loop:
            :return:
            """
            app._es_client_service: ElasticsearchClientService = ElasticsearchClientService(app, loop)

        @self.listener("after_server_stop")
        async def shutdown(app: SanicElasticsearch, loop):
            """
            Trigger clean shutdown of ES client
            :param app:
            :param loop:
            :return:
            """
            await app._es_client_service.shutdown()

    @property
    def elasticsearch_client(self) -> Elasticsearch:
        """
        Return the correct client instance
        :return:
        """
        return self._es_client_service.client
