"""
This file contains utility methods for performing search queries using abstract search engines and clients
"""
from json import loads
from typing import ClassVar, List
from elasticsearch.exceptions import ConnectionError

from sanic.exceptions import ServerError, InvalidUsage

from dp4py_logging.time import timeit

from dp_conceptual_search.log import logger
from dp_conceptual_search.app.search_app import SearchApp
from dp_conceptual_search.config.config import FASTTEXT_CONFIG
from dp_conceptual_search.api.search.list_type import ListType
from dp_conceptual_search.api.request.ons_request import ONSRequest

from dp_conceptual_search.ons.search.index import Index
from dp_conceptual_search.ons.search.sort_fields import SortField
from dp_conceptual_search.ons.search.exceptions import UnknownTypeFilter
from dp_conceptual_search.ons.search.content_type import AvailableContentTypes
from dp_conceptual_search.ons.search.type_filter import build_filter_functions
from dp_conceptual_search.ons.search.response.search_result import SearchResult
from dp_conceptual_search.ons.search.response.client.ons_response import ONSResponse
from dp_conceptual_search.ons.search.type_filter import AvailableTypeFilters, TypeFilter
from dp_conceptual_search.ons.search.client.abstract_search_engine import AbstractSearchEngine
from dp_conceptual_search.ons.conceptual.client.conceptual_search_engine import ConceptualSearchEngine

from dp_conceptual_search.search.client.exceptions import RequestSizeExceededException


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

    @timeit
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

        try:
            engine: AbstractSearchEngine = engine.paginate(page, page_size)
        except RequestSizeExceededException as e:
            # Log and raise a 400 BAD_REQUEST
            message = "Requested page size exceeds max allowed: '{0}'".format(e)
            logger.error(request.request_id, message, exc_info=e)
            raise InvalidUsage(message)

        # Add any type filters
        if type_filters_raw is not None:
            if not isinstance(type_filters_raw, list):
                type_filters_raw = [type_filters_raw]
            try:
                type_filters = AvailableTypeFilters.from_string_list(type_filters_raw)
                engine: AbstractSearchEngine = engine.type_filter(type_filters)
            except UnknownTypeFilter as e:
                message = "Received unknown type filter: '{0}'".format(e.unknown_type_filter)
                logger.error(request.request_id, message, exc_info=e)
                raise InvalidUsage(message)

        # Execute
        try:
            logger.trace(request.request_id, "Executing proxy query", extra={
                "query": engine.to_dict()
            })
            response: ONSResponse = await engine.execute()
        except ConnectionError as e:
            message = "Unable to connect to Elasticsearch cluster to perform proxy query request"
            logger.error(request.request_id, message, e)
            raise ServerError(message)

        search_result: SearchResult = response.to_content_query_search_result(page, page_size, sort_by)

        return search_result

    @timeit
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

            logger.trace(request.request_id, "Executing departments query", extra={
                "query": engine.to_dict()
            })
            response: ONSResponse = await engine.execute()
        except ConnectionError as e:
            message = "Unable to connect to Elasticsearch cluster to perform departments query request"
            logger.error(request.request_id, message, exc_info=e)
            raise ServerError(message)

        search_result: SearchResult = response.to_departments_query_search_result(page, page_size)

        return search_result

    @timeit
    async def content_query(self, request: ONSRequest, list_type: ListType) -> SearchResult:
        """
        Executes the ONS content query using the given SearchEngine class
        :param request:
        :param list_type:
        :return:
        """
        # Initialise the search engine
        engine: AbstractSearchEngine = self.get_search_engine_instance()

        # Perform the query
        search_term = request.get_search_term()
        page = request.get_current_page()
        page_size = request.get_page_size()
        sort_by: SortField = request.get_sort_by()
        type_filters: List[TypeFilter] = request.get_type_filters(list_type)

        # Build filter functions
        filter_functions: List[AvailableContentTypes] = build_filter_functions(type_filters)

        try:
            kwargs = {}
            if isinstance(engine, ConceptualSearchEngine):
                labels, search_vector = await engine.conceptual_search_params(search_term,
                                                                              FASTTEXT_CONFIG.num_labels,
                                                                              FASTTEXT_CONFIG.threshold)
                kwargs['labels'] = labels
                kwargs['search_vector'] = search_vector

            engine: AbstractSearchEngine = engine.content_query(search_term, page, page_size, sort_by=sort_by,
                                                                filter_functions=filter_functions,
                                                                type_filters=type_filters,
                                                                **kwargs)

            logger.trace(request.request_id, "Executing content query", extra={
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

    @timeit
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
            kwargs = {}
            if isinstance(engine, ConceptualSearchEngine):
                labels, search_vector = await engine.conceptual_search_params(search_term,
                                                                              FASTTEXT_CONFIG.num_labels,
                                                                              FASTTEXT_CONFIG.threshold)
                kwargs['labels'] = labels
                kwargs['search_vector'] = search_vector

            engine: AbstractSearchEngine = engine.type_counts_query(search_term, **kwargs)

            logger.trace(request.request_id, "Executing type counts query", extra={
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

    @timeit
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

            logger.trace(request.request_id, "Executing featured result query", extra={
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
