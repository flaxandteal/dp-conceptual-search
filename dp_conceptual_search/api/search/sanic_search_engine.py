"""
This file contains utility methods for performing search queries using abstract search engines and clients
"""
from numpy import ndarray
from typing import ClassVar, List
from elasticsearch.exceptions import ConnectionError

from sanic.exceptions import ServerError, InvalidUsage

from dp4py_logging.time import timeit

from dp_fasttext.client import Client
from dp_fasttext.ml.utils import clean_string, replace_nouns_with_singulars

from dp_conceptual_search.log import logger
from dp_conceptual_search.config.config import FASTTEXT_CONFIG

from dp_conceptual_search.app.search_app import SearchApp
from dp_conceptual_search.api.request.ons_request import ONSRequest

from dp_conceptual_search.ons.search.index import Index
from dp_conceptual_search.ons.search.sort_fields import SortField
from dp_conceptual_search.ons.search.content_type import ContentType
from dp_conceptual_search.ons.search.response.search_result import SearchResult
from dp_conceptual_search.ons.search.response.client.ons_response import ONSResponse
from dp_conceptual_search.search.client.exceptions import RequestSizeExceededException
from dp_conceptual_search.ons.search.client.abstract_search_engine import AbstractSearchEngine
from dp_conceptual_search.ons.search.exceptions import MalformedSearchTerm, UnknownSearchVector
from dp_conceptual_search.ons.conceptual.client import FastTextClientService, ConceptualSearchEngine


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
    async def get_conceptual_search_params(self, request: ONSRequest, search_term: str) -> tuple:
        """
        Queries external fastText server for labels and search vector
        :param request:
        :param search_term:
        :return:
        """
        # Initialise dp-fastText client
        client: Client
        async with FastTextClientService.get_fasttext_client() as client:
            # Set request context header

            headers = {
                Client.REQUEST_ID_HEADER: request.request_id,
                "Connection": "close"
            }

            # First, clean the search term and replace all nouns with singulars
            clean_search_term = replace_nouns_with_singulars(clean_string(search_term))

            if len(clean_search_term) == 0:
                logger.error(request.request_id, "cleaned search term is empty")
                raise MalformedSearchTerm(search_term)

                # Get search vector from dp-fasttext
            search_vector: ndarray = await client.supervised.get_sentence_vector(clean_search_term, headers=headers)

            if search_vector is None:
                logger.error(request.request_id, "Unable to retrieve search vector for query '{0}'".format(search_term))
                raise UnknownSearchVector(search_term)

            # Get keyword labels and their probabilities from dp-fasttext
            num_labels = FASTTEXT_CONFIG.num_labels
            threshold = FASTTEXT_CONFIG.threshold
            labels, probabilities = await client.supervised.predict(search_term, num_labels, threshold, headers=headers)

            return labels, search_vector

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
                labels, search_vector = await self.get_conceptual_search_params(request, search_term)
                kwargs['labels'] = labels
                kwargs['search_vector'] = search_vector

            engine: AbstractSearchEngine = engine.content_query(search_term, page, page_size, sort_by=sort_by,
                                                                filter_functions=type_filters,
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
        type_filters: List[ContentType] = request.get_type_filters()

        try:
            kwargs = {}
            if isinstance(engine, ConceptualSearchEngine):
                labels, search_vector = await self.get_conceptual_search_params(request, search_term)
                kwargs['labels'] = labels
                kwargs['search_vector'] = search_vector

            engine: AbstractSearchEngine = engine.type_counts_query(search_term, type_filters=type_filters, **kwargs)

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
