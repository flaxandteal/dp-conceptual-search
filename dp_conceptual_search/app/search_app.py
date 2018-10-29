"""
This file defines our custom Sanic app class
"""
import logging
from dp4py_sanic.app.server import Server

from dp_conceptual_search.config import CONFIG

from dp_conceptual_search.api.request.ons_request import ONSRequest
from dp_conceptual_search.ml.spelling.spell_checker import SpellChecker
from dp_conceptual_search.app.ml import init_supervised_models, get_supervised_model
from dp_conceptual_search.ml.word_embedding.fastText import UnsupervisedModel, SupervisedModel
from dp_conceptual_search.app.elasticsearch.elasticsearch_client_service import ElasticsearchClientService


class SearchApp(Server):
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

        # Set Logo to None
        self.config.logo = None

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

            logging.info("Initialised Elasticsearch client", extra=elasticsearch_log_data)

            # Now initialise the ML models essential to the APP
            self._initialise_unsupervised_model()
            init_supervised_models(CONFIG.ML.supervised_model_filename)

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
        logging.info("Initialising unsupervised fastText model", extra={
            "model": {
                "filename": CONFIG.ML.unsupervised_model_filename
            }
        })

        self._unsupervised_model = UnsupervisedModel(CONFIG.ML.unsupervised_model_filename)

        logging.info("Successfully initialised unsupervised fastText model", extra={
            "model": {
                "filename": CONFIG.ML.unsupervised_model_filename
            }
        })

    def _initialise_spell_checker(self):
        """
        Initialises the SpellChecker using the unsupervised fastText model
        :return:
        """
        if self.get_unsupervised_model() is not None:
            logging.info("Initialising SpellChecker", extra={
                "model": {
                    "filename": self._unsupervised_model.filename
                }
            })

            self._spell_checker = SpellChecker(self._unsupervised_model)

            logging.info("Successfully initialised SpellChecker", extra={
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
        return get_supervised_model(CONFIG.ML.supervised_model_filename)
