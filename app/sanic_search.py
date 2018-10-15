"""
This file defines our custom Sanic app class
"""
from sanic import Sanic
from sanic.log import logger

from config.config_ml import UNSUPERVISED_MODEL_FILENAME

from ml.word_embedding.fastText import UnsupervisedModel
from ml.spelling.spell_checker import SpellChecker

from app.elasticsearch.elasticsearch_client_service import ElasticsearchClientService


class SanicSearch(Sanic):
    def __init__(self, *args, **kwargs):
        from api.request.ons_request import ONSRequest
        # Initialise APP with custom ONSRequest class
        super(SanicSearch, self).__init__(*args, request_class=ONSRequest, **kwargs)

        # Attach an Elasticsearh client
        self._elasticsearch = None
        self._spell_checker = None

        # Initialise unsupervised model member
        self._unsupervised_model = None

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
            self._unsupervised_model = UnsupervisedModel(UNSUPERVISED_MODEL_FILENAME)

            logger.info("Initialised unsupervised fastText model: {fname}".format(fname=UNSUPERVISED_MODEL_FILENAME))

            # Initialise spell checker
            self._spell_checker = SpellChecker(self._unsupervised_model)

            logger.info("Initialised spell checker")

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
        """
        Return the Elasticsearch client
        :return:
        """
        return self._elasticsearch

    @property
    def spell_checker(self) -> SpellChecker:
        """
        Returns the spell checker
        :return:
        """
        return self._spell_checker

    def get_unsupervised_model(self) -> UnsupervisedModel:
        """
        Returns the cached unsupervised model
        :return:
        """
        return self.__unsupervised_model
