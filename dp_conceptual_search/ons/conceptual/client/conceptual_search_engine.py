"""
Implementation of conceptual search client
"""
import logging
from typing import List
from numpy import ndarray

from dp_conceptual_search.config.config import SEARCH_CONFIG
from dp_conceptual_search.search.search_type import SearchType
from dp_conceptual_search.ons.search.exceptions import InvalidUsage
from dp_conceptual_search.ons.search.client.search_engine import SearchEngine
from dp_conceptual_search.ons.search.queries.ons_query_builders import build_type_counts_query
from dp_conceptual_search.ons.conceptual.queries.ons_query_builders import build_content_query
from dp_conceptual_search.ons.search import SortField, AvailableTypeFilters, TypeFilter, AvailableContentTypes


class ConceptualSearchEngine(SearchEngine):

    def content_query(self, search_term: str, current_page: int, size: int,
                      sort_by: SortField = SortField.relevance,
                      highlight: bool = True,
                      filter_functions: List[AvailableContentTypes] = None,
                      type_filters: List[TypeFilter] = None,
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
            logging.debug("SortField != relevance, conceptual search is disabled", extra={
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

        if type_filters is None:
            type_filters = AvailableTypeFilters.all()

        # Build the query
        query = build_content_query(search_term, labels, search_vector)

        # Build the content query
        s: ConceptualSearchEngine = self._clone() \
            .query(query) \
            .paginate(current_page, size) \
            .type_filter(type_filters) \
            .search_type(SearchType.DFS_QUERY_THEN_FETCH)

        if highlight:
            s: SearchEngine = s.apply_highlight_fields()

        return s

    def type_counts_query(self, search_term, type_filters: List[TypeFilter] = None, **kwargs):
        """
        Builds the ONS conceptual type counts query, responsible providing counts by content type
        :param search_term:
        :param type_filters:
        :param kwargs:
        :return:
        """
        labels: List[str] = kwargs.get("labels", None)
        search_vector: ndarray = kwargs.get("search_vector", None)

        if type_filters is None:
            type_filters = AvailableTypeFilters.all()

        # Build the content query with no type filters, function scores or sorting
        s: SearchEngine = self.content_query(search_term, self.default_page_number,
                                             SEARCH_CONFIG.results_per_page,
                                             type_filters=type_filters, highlight=False,
                                             labels=labels, search_vector=search_vector)

        # Build the aggregations
        aggregations = build_type_counts_query()

        # Setup the aggregations bucket
        s.aggs.bucket(self.agg_bucket, aggregations)

        return s
