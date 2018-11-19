"""
This file contains utility methods for performing search queries using abstract search engines and clients
"""
from typing import ClassVar, List

from elasticsearch.exceptions import ConnectionError

from sanic.exceptions import ServerError, InvalidUsage

from dp_conceptual_search.api.log import logger
from dp_conceptual_search.api.request.ons_request import ONSRequest

from dp_conceptual_search.app.search_app import SearchApp

from dp_conceptual_search.search.client.exceptions import RequestSizeExceededException

from dp_conceptual_search.ons.search.index import Index
from dp_conceptual_search.ons.search.sort_fields import SortField
from dp_conceptual_search.ons.search.content_type import ContentType
from dp_conceptual_search.ons.search.response.search_result import SearchResult
from dp_conceptual_search.ons.search.response.client.ons_response import ONSResponse
from dp_conceptual_search.ons.search.client.abstract_search_engine import AbstractSearchEngine


class SanicSearchEngine(object):
    def __init__(self, app: SearchApp, search_engine_cls: ClassVar[AbstractSearchEngine], index: Index):
        """
        Helper class for working with abstract search engine instances
        :param app:
        :param search_engine_cls:
        :param index:
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

        try:
            engine: AbstractSearchEngine = engine.departments_query(search_term, page, page_size)

            logger.debug(request.request_id, "Executing departments query", extra={
                "query": engine.to_dict()
            })
            response: ONSResponse = await engine.execute()
        except ConnectionError as e:
            message = "Unable to connect to Elasticsearch cluster to perform departments query request"
            logger.error(request.request_id, message, exc_info=e)
            raise ServerError(message)

        search_result: SearchResult = response.to_departments_query_search_result(page, page_size)

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
        type_filters: List[ContentType] = request.get_type_filters()

        try:
            # Pass the same content types as both filters and filter boosts (type_filters and filter_functions,
            # respectively).
            engine: AbstractSearchEngine = engine.content_query(search_term, page, page_size, sort_by=sort_by,
                                                                filter_functions=type_filters,
                                                                type_filters=type_filters)

            logger.debug(request.request_id, "Executing content query", extra={
                "query": engine.to_dict()
            })
            response: ONSResponse = await engine.execute()
        except ConnectionError as e:
            message = "Unable to connect to Elasticsearch cluster to perform content query request"
            logger.error(request.request_id, message, exc_info=e)
            raise ServerError(message)
        except RequestSizeExceededException as e:
            # Log and raise a 400 BAD_REQUEST
            message = "Requested page size exceeds max allowed: '{0}'".format(e)
            logger.error(request.request_id, message, exc_info=e)
            raise InvalidUsage(message)

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
        type_filters: List[ContentType] = request.get_type_filters()

        try:
            engine: AbstractSearchEngine = engine.type_counts_query(search_term, type_filters=type_filters)

            logger.debug(request.request_id, "Executing type counts query", extra={
                "query": engine.to_dict()
            })
            response: ONSResponse = await engine.execute()
        except ConnectionError as e:
            message = "Unable to connect to Elasticsearch cluster to perform type counts query request"
            logger.error(request.request_id, message, exc_info=e)
            raise ServerError(message)
        except RequestSizeExceededException as e:
            # Log and raise a 400 BAD_REQUEST
            message = "Requested page size exceeds max allowed: '{0}'".format(e)
            logger.error(request.request_id, message, exc_info=e)
            raise InvalidUsage(message)

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
            engine: AbstractSearchEngine = engine.featured_result_query(search_term)

            logger.debug(request.request_id, "Executing featured result query", extra={
                "query": engine.to_dict()
            })
            response: ONSResponse = await engine.execute()
        except ConnectionError as e:
            message = "Unable to connect to Elasticsearch cluster to perform featured result query request"
            logger.error(request.request_id, message, exc_info=e)
            raise ServerError(message)
        except RequestSizeExceededException as e:
            # Log and raise a 400 BAD_REQUEST
            message = "Requested page size exceeds max allowed: '{0}'".format(e)
            logger.error(request.request_id, message, exc_info=e)
            raise InvalidUsage(message)

        search_result: SearchResult = response.to_featured_result_query_search_result()

        return search_result
