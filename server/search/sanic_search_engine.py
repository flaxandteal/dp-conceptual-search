"""
This file contains utility methods for performing search queries using abstract search engines and clients
"""
from typing import ClassVar

from ons.search.index import Index
from ons.search.client.abstract_search_engine import AbstractSearchEngine

from server.request.ons_request import ONSRequest
from server.sanic_elasticsearch import SanicElasticsearch


class SanicSearchEngine(object):
    def __init__(self, app: SanicElasticsearch, search_engine_cls: ClassVar[AbstractSearchEngine], index: Index):
        """
        Helper class for working with abstract search engine instances
        :param app:
        :param search_engine_cls:
        """
        self.app = app
        self.index = index
        self._search_engine_cls = search_engine_cls

    def get_search_engine_instance(self) -> AbstractSearchEngine:
        """
        Returns an instance of the desired SearchEngine class
        :return:
        """
        return self._search_engine_cls(using=self.app.elasticsearch_client, index=self.index.value)

    def content_query(self, request: ONSRequest):
        """
        Executes the ONS content query using the given SearchEngine class
        :param request:
        :return:
        """
        pass
