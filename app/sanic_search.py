"""
This file defines our custom Sanic app class
"""
from sanic.log import logger

from sanic import Sanic

from config.config_ml import UNSUPERVISED_MODEL_FILENAME

from api.request.ons_request import ONSRequest
from app.ml.ml_models import Models
from ml.word_embedding.fastText import UnsupervisedModel
from app.elasticsearch.elasticsearch_client_service import ElasticsearchClientService


class SanicSearch(Sanic):
    def __init__(self, *args, **kwargs):
        # Initialise APP with custom ONSRequest class
        super(SanicSearch, self).__init__(*args, request_class=ONSRequest, **kwargs)

        # Attach an Elasticsearh client
        self._elasticsearch = None

        # Create cache for ML models
        self._models = {}

        @self.listener("after_server_start")
        async def init(app: SanicSearch, loop):
            """
            Initialise the ES client and ML models after api start (when the ioloop exists)
            :param app:
            :param loop:
            :return:
            """
            # First, initialise Elasticsearch
            app._elasticsearch: ElasticsearchClientService = ElasticsearchClientService(app, loop)

            elasticsearch_log_data = {
                "data": {
                    "elasticsearch.host": self.elasticsearch.elasticsearch_host,
                    "elasticsearch.async": self.elasticsearch.elasticsearch_async_enabled,
                    "elasticsearch.timeout": self.elasticsearch.elasticsearch_timeout
                }
            }

            logger.info("Initialised Elasticsearch client", extra=elasticsearch_log_data)

            # Now initialise the ML models essential to the APP
            self._models[Models.ONS_UNSUPERVISED_MODEL] = UnsupervisedModel(UNSUPERVISED_MODEL_FILENAME)

            logger.info("Initialised unsupervised fastText model: {fname}".format(fname=UNSUPERVISED_MODEL_FILENAME))

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

    def get_unsupervised_model(self) -> UnsupervisedModel:
        """
        Returns the cached unsupervised model
        :return:
        """
        return self._models.get(Models.ONS_UNSUPERVISED_MODEL)
