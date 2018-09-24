"""
This file contains utility methods for performing search queries using abstract search engines and clients
"""
from typing import ClassVar
from json import loads

from elasticsearch.exceptions import ConnectionError

from api.log import logger
from sanic.exceptions import ServerError, InvalidUsage

from ons.search.index import Index
from ons.search.sort_fields import SortField
from ons.search.type_filter import TypeFilters
from ons.search.response.search_result import SearchResult
from ons.search.response.client.ons_response import ONSResponse
from ons.search.client.abstract_search_engine import AbstractSearchEngine
from ons.search.exceptions.unknown_type_filter_exception import UnknownTypeFilter

from api.request.ons_request import ONSRequest
from app.sanic_elasticsearch import SanicElasticsearch


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

    async def proxy(self, request: ONSRequest) -> SearchResult:
        """
        Proxy an Elasticsearch query over HTTP
        :param request:
        :return:
        """
        # Initialise the search engine
        engine: AbstractSearchEngine = self.get_search_engine_instance()

        # Parse the request body for a valid Elasticsearch query
        body: dict = request.get_elasticsearch_query()

        # Parse query and filters
        query: dict = loads(body.get("query"))
        type_filters_raw = body.get("filter")

        # Update the search engine with the query JSON
        engine.update_from_dict(query)

        # Extract paginator params
        page = request.get_current_page()
        page_size = request.get_page_size()
        sort_by = request.get_sort_by()

        # Add any type filters
        if type_filters_raw is not None:
            if not isinstance(type_filters_raw, list):
                type_filters_raw = [type_filters_raw]
            try:
                type_filters = TypeFilters.from_string_list(type_filters_raw)
                engine: AbstractSearchEngine = engine.type_filter(type_filters)
            except UnknownTypeFilter as e:
                message = "Received unknown type filter: '{0}'".format(e.unknown_type_filter)
                logger.error(request, message, exc_info=e)
                raise InvalidUsage(message)

        # Execute
        try:
            response: ONSResponse = await engine.execute()
        except ConnectionError as e:
            message = "Unable to connect to Elasticsearch cluster to perform proxy query request"
            logger.error(request, message, e)
            raise ServerError(message)

        search_result: SearchResult = response.to_content_query_search_result(page, page_size, sort_by)

        return search_result

    async def departments_query(self, request: ONSRequest) -> SearchResult:
        """
        Executes the ONS departments query using the given SearchEngine class
        :param request:
        :return:
        """
        # Initialise the search engine
        engine: AbstractSearchEngine = self.get_search_engine_instance()

        # Perform the query
        search_term = request.get_search_term()
        page = request.get_current_page()
        page_size = request.get_page_size()
        sort_by: SortField = request.get_sort_by()

        try:
            response: ONSResponse = await engine.departments_query(search_term, page, page_size).execute()
        except ConnectionError as e:
            message = "Unable to connect to Elasticsearch cluster to perform departments query request"
            logger.error(request, message, e)
            raise ServerError(message)

        search_result: SearchResult = response.to_content_query_search_result(page, page_size, sort_by)

        return search_result

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
        sort_by: SortField = request.get_sort_by()

        try:
            response: ONSResponse = await engine.content_query(search_term, page, page_size, sort_by=sort_by).execute()
        except ConnectionError as e:
            message = "Unable to connect to Elasticsearch cluster to perform content query request"
            logger.error(request, message, e)
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
            logger.error(request, message, e)
            raise ServerError(message)

        search_result: SearchResult = response.to_type_counts_query_search_result()

        return search_result

    async def featured_result_query(self, request: ONSRequest):
        """
        Executes the ONS featured result query using the given SearchEngine class
        :param request:
        :return:
        """
        engine: AbstractSearchEngine = self.get_search_engine_instance()

        # Perform the query
        search_term = request.get_search_term()

        try:
            response: ONSResponse = await engine.featured_result_query(search_term).execute()
        except ConnectionError as e:
            message = "Unable to connect to Elasticsearch cluster to perform featured result query request"
            logger.error(request, message, e)
            raise ServerError(message)

        search_result: SearchResult = response.to_featured_result_query_search_result()

        return search_result
