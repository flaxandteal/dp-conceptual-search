"""
This file contains utility methods for performing search queries using abstract search engines and clients
"""
from typing import ClassVar

from elasticsearch.exceptions import ConnectionError

from sanic.log import logger
from sanic.exceptions import ServerError

from ons.search.index import Index
from ons.search.sort_fields import SortFields
from ons.search.response.search_result import SearchResult
from ons.search.response.client.ons_response import ONSResponse
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
        return self._search_engine_cls(using=self.app.elasticsearch.client, index=self.index.value)

    async def content_query(self, request: ONSRequest) -> SearchResult:
        """
        Executes the ONS content query using the given SearchEngine class
        :param request:
        :return:
        """
        # Initialise the search engine
        engine: AbstractSearchEngine = self.get_search_engine_instance()

        # Perform the query
        search_term = request.get_search_term()
        page = request.get_current_page()
        page_size = request.get_page_size()
        sort_by: SortFields = request.get_sort_by()

        try:
            response: ONSResponse = await engine.content_query(search_term, page, page_size, sort_by=sort_by).execute()
        except ConnectionError as e:
            message = "Unable to connect to Elasticsearch cluster to perform type counts query request"
            logger.error(message, exc_info=e)
            raise ServerError(message)

        search_result: SearchResult = response.to_content_query_search_result(page, page_size, sort_by)

        return search_result

    async def type_counts_query(self, request: ONSRequest) -> SearchResult:
        """
        Executes the ONS type counts query using the given SearchEngine class
        :param request:
        :return:
        """
        engine: AbstractSearchEngine = self.get_search_engine_instance()

        # Perform the query
        search_term = request.get_search_term()

        try:
            response: ONSResponse = await engine.type_counts_query(search_term).execute()
        except ConnectionError as e:
            message = "Unable to connect to Elasticsearch cluster to perform type counts query request"
            logger.error(message, exc_info=e)
            raise ServerError(message)

        search_result: SearchResult = response.to_type_counts_query_search_result()

        return search_result
