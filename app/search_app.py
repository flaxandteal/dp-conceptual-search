"""
This file defines our custom Sanic app class
"""
from sanic import Sanic
from sanic.log import logger

from config.config_ml import UNSUPERVISED_MODEL_FILENAME, SUPERVISED_MODEL_FILENAME

from ml.spelling.spell_checker import SpellChecker
from ml.word_embedding.fastText import UnsupervisedModel, SupervisedModel

from api.request.ons_request import ONSRequest

from app.ml import init_supervised_models, get_supervised_model
from app.elasticsearch.elasticsearch_client_service import ElasticsearchClientService


class SearchApp(Sanic):
    def __init__(self, *args, **kwargs):
        # Initialise APP with custom ONSRequest class
        super(SearchApp, self).__init__(*args, request_class=ONSRequest, **kwargs)

        # Attach an Elasticsearh client
        self._elasticsearch = None

        # Initialise (un)supervised model member
        self._unsupervised_model = None
        self._supervised_model = None

        # Initialise spell check member
        self._spell_checker = None

        @self.listener("after_server_start")
        async def init(app: SearchApp, loop):
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
            self._initialise_unsupervised_model()
            init_supervised_models(SUPERVISED_MODEL_FILENAME)

            # Initialise spell checker
            self._initialise_spell_checker()

        @self.listener("after_server_stop")
        async def shutdown(app: SearchApp, loop):
            """
            Trigger clean shutdown of ES client
            :param app:
            :param loop:
            :return:
            """
            await app.elasticsearch.shutdown()

    def _initialise_unsupervised_model(self):
        """
        Initialises the unsupervised fastText .vec model
        :return:
        """
        logger.info("Initialising unsupervised fastText model", extra={
            "model": {
                "filename": UNSUPERVISED_MODEL_FILENAME
            }
        })

        self._unsupervised_model = UnsupervisedModel(UNSUPERVISED_MODEL_FILENAME)

        logger.info("Successfully initialised unsupervised fastText model", extra={
            "model": {
                "filename": UNSUPERVISED_MODEL_FILENAME
            }
        })

    def _initialise_spell_checker(self):
        """
        Initialises the SpellChecker using the unsupervised fastText model
        :return:
        """
        if self.get_unsupervised_model() is not None:
            logger.info("Initialising SpellChecker", extra={
                "model": {
                    "filename": self._unsupervised_model.filename
                }
            })

            self._spell_checker = SpellChecker(self._unsupervised_model)

            logger.info("Successfully initialised SpellChecker", extra={
                "model": {
                    "filename": self._unsupervised_model.filename
                }
            })

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
        return self._unsupervised_model

    def get_supervised_model(self) -> SupervisedModel:
        """
        Returns the cached supervised model
        :return:
        """
        return get_supervised_model(SUPERVISED_MODEL_FILENAME)
