"""
Implementation of conceptual search client
"""
import logging
from typing import List
from numpy import ndarray

from dp_conceptual_search.search.search_type import SearchType
from dp_conceptual_search.search.dsl.vector_script_score import VectorScriptScore

from dp_conceptual_search.ons.search import SortField, ContentType
from dp_conceptual_search.ons.search.exceptions import InvalidUsage
from dp_conceptual_search.ons.search.fields import AvailableFields, Field
from dp_conceptual_search.ons.search.client.search_engine import SearchEngine
from dp_conceptual_search.ons.search.queries.ons_query_builders import build_type_counts_query
from dp_conceptual_search.ons.conceptual.queries.ons_query_builders import build_content_query


class ConceptualSearchEngine(SearchEngine):
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
        :param filter_functions: content types to generate filter scores for (content type boosting)
        :param type_filters: content types to filter in query
        :param kwargs:
        :return:
        """
        if sort_by is not SortField.relevance:
            logging.debug("sort order is not equal to relevance, conceptual search is disabled", extra={
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
        s: ConceptualSearchEngine = self.content_query(search_term,
                                                       0,  # hard code page number to 0, as it does not impact the aggregations
                                                       0,  # hard code page size to 0, as it does not impact the aggregations
                                                       type_filters=type_filters,
                                                       highlight=False,
                                                       labels=labels,
                                                       search_vector=search_vector)

        # Build the aggregations
        aggregations = build_type_counts_query()

        # Setup the aggregations bucket
        s.aggs.bucket(self.agg_bucket, aggregations)

        return s
