from typing import List

from ons.search.sort_fields import SortFields
from ons.search.type_filter import TypeFilters
from ons.search.content_type import ContentType
from ons.search.client.abstract_search_engine import AbstractSearchEngine


class SearchEngine(AbstractSearchEngine):
    """
    Implementation of the ONS search engine
    """
    default_page_number = 1
    agg_bucket = "docCounts"

    def departments_query(self, search_term: str, current_page: int, size: int):
        """
        Builds the ONS departments query with pagination
        :param search_term:
        :param current_page:
        :param size:
        :return:
        """
        from core.search.search_type import SearchType
        from ons.search.queries import departments_query

        s: SearchEngine = self._clone() \
            .query(departments_query(search_term)) \
            .paginate(current_page, size) \
            .search_type(SearchType.DFS_QUERY_THEN_FETCH)

        return s

    def content_query(self, search_term: str, current_page: int, size: int,
                      sort_by: SortFields=SortFields.relevance,
                      filter_functions: List[ContentType]=None,
                      type_filters: List[TypeFilters]=None,
                      **kwargs):
        """
        Builds the ONS content query, responsible for populating the SERP
        :param search_term:
        :param current_page:
        :param size:
        :param sort_by:
        :param filter_functions:
        :param type_filters:
        :param kwargs:
        :return:
        """
        if type_filters is None:
            type_filters = list(TypeFilters)

        from core.search.search_type import SearchType
        from ons.search.queries import content_query

        # Build the query dict
        query = content_query(search_term)

        # Add function scores if specified
        if filter_functions is not None:
            from ons.search.queries import function_score_content_query
            query = function_score_content_query(query, filter_functions)

        # Build the content query
        s: SearchEngine = self._clone() \
            .query(query) \
            .paginate(current_page, size) \
            .sort_by(sort_by) \
            .type_filter(type_filters) \
            .search_type(SearchType.DFS_QUERY_THEN_FETCH)

        return s

    def type_counts_query(self, search_term, **kwargs):
        """
        Builds the ONS type counts query, responsible providing counts by content type
        :param search_term:
        :param kwargs:
        :return:
        """
        from ons.search.queries import type_counts_query
        from ons.search.paginator import RESULTS_PER_PAGE

        # Build the content query with no type filters, function scores or sorting
        s: SearchEngine = self.content_query(search_term, self.default_page_number, RESULTS_PER_PAGE)

        # Build the aggregations
        aggregations = type_counts_query()

        # Setup the aggregations bucket
        s.aggs.bucket(self.agg_bucket, aggregations)

        return s

    def featured_result_query(self, search_term):
        pass
