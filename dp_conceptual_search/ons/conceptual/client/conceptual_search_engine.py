"""
Implementation of conceptual search client
"""
import logging
from uuid import uuid4
from numpy import ndarray
from typing import List, Tuple

from elasticsearch_dsl.response.hit import Hit

from dp_fasttext.client import Client
from dp_fasttext.ml.utils import clean_string, replace_nouns_with_singulars, decode_float_list, encode_float_list

from dp_conceptual_search.log import logger

from dp_conceptual_search.config.config import SEARCH_CONFIG
from dp_conceptual_search.search.search_type import SearchType
from dp_conceptual_search.search.dsl.vector_script_score import VectorScriptScore

from dp_conceptual_search.ons.search import SortField, ContentType
from dp_conceptual_search.ons.search.exceptions import InvalidUsage
from dp_conceptual_search.ons.search.fields import AvailableFields, Field
from dp_conceptual_search.ons.search.client.search_engine import SearchEngine
from dp_conceptual_search.ons.search.response.client.ons_response import ONSResponse
from dp_conceptual_search.ons.search.queries.ons_query_builders import build_type_counts_query
from dp_conceptual_search.ons.search.exceptions import MalformedSearchTerm, UnknownSearchVector

from dp_conceptual_search.ons.conceptual.client.fasttext_client import FastTextClientService
from dp_conceptual_search.ons.conceptual.queries.ons_query_builders import build_content_query


class ConceptualSearchEngine(SearchEngine):

    CONNECTION_HEADER = "Connection"
    CONNECTION_CLOSE = "close"
    EMBEDDING_VECTOR: Field = AvailableFields.EMBEDDING_VECTOR.value

    def vector_script_score(self, vector: ndarray) -> VectorScriptScore:
        """
        Wrapper for building a script score function using the embedding vector field
        :param vector:
        :return:
        """
        return VectorScriptScore(self.EMBEDDING_VECTOR.name, vector, cosine=True)

    def content_query(self, search_term: str, current_page: int, size: int,
                      sort_by: SortField = SortField.relevance,
                      highlight: bool = True,
                      filter_functions: List[ContentType] = None,
                      type_filters: List[ContentType] = None,
                      **kwargs):
        """
        Builds the ONS conceptual search content query, responsible for populating the SERP
        :param search_term:
        :param current_page:
        :param size:
        :param sort_by:
        :param highlight:
        :param filter_functions:
        :param type_filters:
        :param kwargs:
        :return:
        """
        if sort_by is not SortField.relevance:
            logging.debug("SortField != relevance, reverting to standard content query", extra={
                "query": search_term,
                "sort_by": sort_by.name
            })
            return super(ConceptualSearchEngine, self).content_query(search_term,
                                                                     current_page,
                                                                     size,
                                                                     sort_by=sort_by,
                                                                     highlight=highlight,
                                                                     filter_functions=filter_functions,
                                                                     type_filters=type_filters,
                                                                     **kwargs)

        labels: List[str] = kwargs.get("labels", None)
        if labels is None or not isinstance(labels, list):
            raise InvalidUsage("Must supply 'labels: List[str]' argument for conceptual search")

        search_vector: ndarray = kwargs.get("search_vector", None)
        if search_vector is None or not isinstance(search_vector, ndarray):
            raise InvalidUsage("Must supply 'search_vector: np.ndarray' argument for conceptual search")

        vector_script_score = self.vector_script_score(search_vector)

        # Build the query
        query = build_content_query(search_term, labels, vector_script_score)

        # Build the content query
        s: ConceptualSearchEngine = self._clone() \
            .query(query) \
            .paginate(current_page, size) \
            .search_type(SearchType.DFS_QUERY_THEN_FETCH) \
            .exclude_fields_from_source(self.EMBEDDING_VECTOR)

        if type_filters is not None:
            s: ConceptualSearchEngine = s.type_filter(type_filters)

        if highlight:
            s: SearchEngine = s.apply_highlight_fields()

        return s

    def type_counts_query(self, search_term, type_filters: List[ContentType] = None, **kwargs):
        """
        Builds the ONS conceptual type counts query, responsible providing counts by content type
        :param search_term:
        :param type_filters:
        :param kwargs:
        :return:
        """
        labels: List[str] = kwargs.get("labels", None)
        search_vector: ndarray = kwargs.get("search_vector", None)

        # Build the content query with no type filters, function scores or sorting
        s: SearchEngine = self.content_query(search_term,
                                             self.default_page_number,
                                             SEARCH_CONFIG.results_per_page,
                                             type_filters=type_filters,
                                             highlight=False,
                                             labels=labels,
                                             search_vector=search_vector)

        # Build the aggregations
        aggregations = build_type_counts_query()

        # Setup the aggregations bucket
        s.aggs.bucket(self.agg_bucket, aggregations)

        return s

    async def embedding_vector_for_uri(self, uri: str) -> ndarray:
        """
        Returns the embedding vector for the page at the given uri
        :param uri:
        :return:
        """
        # First, build the query
        s: ConceptualSearchEngine = self.match_by_uri(uri)

        # Execute the query
        response: ONSResponse = await s.execute()

        # Check we got back exactly 1 hit
        if len(response) != 1:
            raise Exception("Expected exactly one hit for uri '{0}', got {1}".format(uri, len(response)))

        # Get the hit
        hit: Hit = response[0]
        # Convert to dict
        hit_dict: dict = hit.to_dict()

        # Get the embedding vector
        if self.EMBEDDING_VECTOR.name not in hit_dict:
            raise IndexError("Embedding vector field '{0}' not found in hit for uri '{1}'".format(
                self.EMBEDDING_VECTOR.name, uri
            ))

        encoded_embedding_vector: str = hit_dict.get(self.EMBEDDING_VECTOR.name)
        if not isinstance(encoded_embedding_vector, str):
            raise Exception("Expected string embedding vector, got '{0}'".format(type(encoded_embedding_vector)))

        # Decode the string
        return decode_float_list(encoded_embedding_vector)

    def get_fasttext_headers(self, context: str):
        """
        Build and return headers for fastText client
        :param context:
        :return:
        """
        return {
            Client.REQUEST_ID_HEADER: context,
            self.CONNECTION_HEADER: self.CONNECTION_CLOSE
        }

    async def similar_by_vector(self, vector: ndarray, num_labels: int, **kwargs) -> list:
        """
        Initialises a fastText client and makes a HTTP request to get words similar by vector
        :param vector:
        :param num_labels:
        :return:
        """
        # Get request context
        context: str = kwargs.get("context", str(uuid4()))

        client: Client
        async with FastTextClientService.get_fasttext_client() as client:
            # Encode vector
            encoded_vector = encode_float_list(list(vector.tolist()))

            # Generate headers
            headers = self.get_fasttext_headers(context)

            similar_words = await client.unsupervised.similar_by_vector(encoded_vector, num_labels, headers=headers)

            return similar_words

    async def conceptual_search_params(self, search_term: str, num_labels: int, threshold: float, **kwargs) -> \
            Tuple[List[str], ndarray]:
        """
        Queries external fastText server for labels and search vector
        :param search_term:
        :param num_labels:
        :param threshold:
        :return:
        """
        # Get/generate request context
        context = kwargs.get("context", str(uuid4()))

        # Initialise dp-fastText client
        client: Client
        async with FastTextClientService.get_fasttext_client() as client:
            # Set request context header

            headers = self.get_fasttext_headers(context)

            # First, clean the search term and replace all nouns with singulars
            clean_search_term = replace_nouns_with_singulars(clean_string(search_term))

            if len(clean_search_term) == 0:
                logger.error(context, "cleaned search term is empty")
                raise MalformedSearchTerm(search_term)

            # Get search vector from dp-fasttext
            search_vector: ndarray = await client.supervised.get_sentence_vector(clean_search_term, headers=headers)

            if search_vector is None:
                logger.error(context, "Unable to retrieve search vector for query '{0}'".format(search_term))
                raise UnknownSearchVector(search_term)

            # Get keyword labels and their probabilities from dp-fasttext
            labels, probabilities = await client.supervised.predict(search_term, num_labels, threshold, headers=headers)

            return labels, search_vector