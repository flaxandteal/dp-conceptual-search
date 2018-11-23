"""
This file contains utility methods for performing search queries using abstract search engines and clients
"""
from typing import ClassVar, List

from elasticsearch.exceptions import ConnectionError

from sanic.exceptions import ServerError, InvalidUsage

from dp4py_logging.time import timeit

from dp_conceptual_search.config.config import FASTTEXT_CONFIG

from dp_conceptual_search.log import logger
from dp_conceptual_search.app.search_app import SearchApp
from dp_conceptual_search.api.request import ONSRequest
from dp_conceptual_search.search.client.exceptions import RequestSizeExceededException

from dp_conceptual_search.ons.search.index import Index
from dp_conceptual_search.ons.search.sort_fields import SortField
from dp_conceptual_search.ons.search.content_type import ContentType
from dp_conceptual_search.ons.conceptual.client import ConceptualSearchEngine
from dp_conceptual_search.ons.search.response.search_result import SearchResult
from dp_conceptual_search.ons.search.response.client.ons_response import ONSResponse
from dp_conceptual_search.ons.search.client.abstract_search_engine import AbstractSearchEngine


async def execute(request: ONSRequest, engine: AbstractSearchEngine) -> ONSResponse:
    """
    Executes a search query and logs known exceptions
    :param request:
    :param engine:
    :return:
    """
    try:
        return await engine.execute()
    except ConnectionError as e:
        message = "Unable to connect to Elasticsearch cluster to perform content query request"
        logger.error(request.request_id, message, exc_info=e)
        raise ServerError(message)


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

        engine: AbstractSearchEngine = engine.departments_query(search_term, page, page_size)

        logger.trace(request.request_id, "Executing departments query", extra={
            "query": engine.to_dict()
        })
        response: ONSResponse = await execute(request, engine)

        search_result: SearchResult = response.to_departments_query_search_result(page, page_size)

        return search_result

    @timeit
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
            kwargs = {}
            if isinstance(engine, ConceptualSearchEngine):
                labels, search_vector = await engine.conceptual_search_params(search_term,
                                                                              FASTTEXT_CONFIG.num_labels,
                                                                              FASTTEXT_CONFIG.threshold)
                kwargs['labels'] = labels
                kwargs['search_vector'] = search_vector

            logger.debug(request.request_id, "Received content query request", extra={
                "params": {
                    "search_term": search_term,
                    "page": page,
                    "page_size": page_size,
                    "sort_by": sort_by.name,
                    "filters": type_filters,
                    "kwargs": kwargs
                }
            })

            # ND: We pass the same content types as both filters and filter boosts (type_filters and filter_functions,
            # respectively).
            engine: AbstractSearchEngine = engine.content_query(search_term, page, page_size, sort_by=sort_by,
                                                                filter_functions=type_filters,
                                                                type_filters=type_filters,
                                                                **kwargs)

        except RequestSizeExceededException as e:
            # Log and raise a 400 BAD_REQUEST
            message = "Requested page size exceeds max allowed: '{0}'".format(e)
            logger.error(request.request_id, message, exc_info=e)
            raise InvalidUsage(message)

        logger.trace(request.request_id, "Executing content query", extra={
            "query": engine.to_dict()
        })
        response: ONSResponse = await execute(request, engine)

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
        type_filters: List[ContentType] = request.get_type_filters()

        # Attempt to build the query
        try:
            kwargs = {}
            if isinstance(engine, ConceptualSearchEngine):
                labels, search_vector = await engine.conceptual_search_params(search_term,
                                                                              FASTTEXT_CONFIG.num_labels,
                                                                              FASTTEXT_CONFIG.threshold)
                kwargs['labels'] = labels
                kwargs['search_vector'] = search_vector

            logger.debug(request.request_id, "Received type counts query request", extra={
                "params": {
                    "search_term": search_term,
                    "filters": type_filters,
                    "kwargs": kwargs
                }
            })

            engine: AbstractSearchEngine = engine.type_counts_query(search_term, type_filters=type_filters, **kwargs)
        except RequestSizeExceededException as e:
            # Log and raise a 400 BAD_REQUEST
            message = "Requested page size exceeds max allowed: '{0}'".format(e)
            logger.error(request.request_id, message, exc_info=e)
            raise InvalidUsage(message)

        # Execute
        logger.trace(request.request_id, "Executing type counts query", extra={
            "query": engine.to_dict()
        })
        response: ONSResponse = await execute(request, engine)

        search_result: SearchResult = response.to_type_counts_query_search_result()

        return search_result

    @timeit
    async def featured_result_query(self, request: ONSRequest) -> SearchResult:
        """
        Executes the ONS featured result query using the given SearchEngine class
        :param request:
        :return:
        """
        engine: AbstractSearchEngine = self.get_search_engine_instance()

        # Perform the query
        search_term = request.get_search_term()

        logger.debug(request.request_id, "Received featured result query request", extra={
            "params": {
                "search_term": search_term
            }
        })

        try:
            engine: AbstractSearchEngine = engine.featured_result_query(search_term)
        except RequestSizeExceededException as e:
            # Log and raise a 400 BAD_REQUEST
            message = "Requested page size exceeds max allowed: '{0}'".format(e)
            logger.error(request.request_id, message, exc_info=e)
            raise InvalidUsage(message)

        logger.trace(request.request_id, "Executing featured result query", extra={
            "query": engine.to_dict()
        })
        response: ONSResponse = await execute(request, engine)

        search_result: SearchResult = response.to_featured_result_query_search_result()

        return search_result

    @timeit
    async def search_by_uri(self, request: ONSRequest, uri: str) -> SearchResult:
        """
        Search for a page by it's uri
        :param request:
        :param uri:
        :return:
        """
        engine: AbstractSearchEngine = self.get_search_engine_instance()

        # Build the query
        engine: AbstractSearchEngine = engine.match_by_uri(uri)

        # Execute
        response: ONSResponse = await execute(request, engine)

        search_result: SearchResult = response.to_featured_result_query_search_result()
        return search_result

