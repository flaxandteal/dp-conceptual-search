import abc

from core.search.client.async_search import AsyncSearch
from core.search.search_type import SearchType

from ons.search.response import ONSResponse
from ons.search.sort_fields import SortFields
from ons.search.paginator import RESULTS_PER_PAGE

from elasticsearch_dsl import query as Q
from elasticsearch_dsl.aggs import Agg

from typing import List


class AbstractSearchClient(AsyncSearch, abc.ABC):
    """
    Abstract ONS search client which encapsulates several useful methods
    """

    aggs_key = "aggs"
    type_filters = "type_filters"

    def __init__(self, *args, **kwargs):
        super(AsyncSearch, self).__init__(*args, **kwargs)

        self._response_class = ONSResponse

    def paginate(self, current_page: int, size: int):
        s: AbstractSearchClient = self._clone()

        # Calculate from_start param
        from_start = 0 if current_page <= 1 else (current_page - 1) * size
        end = from_start + size

        return s[from_start:end]

    def add_highlight_fields(self, fragment_size: int=0):
        """
        Adds highlight options to the search query
        :return:
        """
        from ons.search.fields import highlight_fields

        field_names = [field.name for field in highlight_fields]

        return self.highlight(
            *field_names,
            fragment_size=fragment_size,
            pre_tags=["<strong>"],
            post_tags=["</strong>"])

    def sort_by(self, sort_by: SortFields):
        """
        Adds sort options to query
        :param sort_by:
        :return:
        """
        from ons.search.sort_fields import query_sort

        return self.sort(
            *query_sort(sort_by)
        )

    def type_filter(self, type_filters):
        """
        Add type filter options to query
        :param type_filters:
        :return:
        """
        if not isinstance(type_filters, list):
            type_filters = [type_filters]

        return self.filter("terms", type=type_filters)

    def build(
            self,
            query: Q.Query,
            aggs: Agg = None,
            current_page: int=1,
            size: int=RESULTS_PER_PAGE,
            sort_by: SortFields=SortFields.relevance,
            search_type: SearchType=SearchType.DFS_QUERY_THEN_FETCH,
            **kwargs):
        """
        Build the full ONS query
        :param query:
        :param current_page:
        :param aggs:
        :param size:
        :param sort_by:
        :param search_type:
        :return:
        """
        # Clone self to add additional params
        s: AbstractSearchClient = self._clone()

        # Set base query
        s: AbstractSearchClient = s.query(query)

        # Setup pagination
        s: AbstractSearchClient = s.paginate(current_page, size)

        # Setup aggregations
        if aggs is not None:
            s.aggs.bucket('docCounts', aggs)

        # Add type filters
        type_filters = kwargs.get(self.type_filters, None)
        if type_filters is not None:
            s: AbstractSearchClient = s.type_filter(type_filters)

        # Add highlights
        s: AbstractSearchClient = s.add_highlight_fields()

        # Sort
        if sort_by is not None:
            s: AbstractSearchClient = s.sort_by(sort_by)

        # Set search type
        s: AbstractSearchClient = s.search_type(search_type)

        return s

    @abc.abstractmethod
    def content_query(
            self,
            search_term: str,
            current_page: int = 1,
            size: int = 10,
            **kwargs):
        """
        ONS search query to populate the SERP
        :param search_term:
        :param current_page:
        :param size:
        :param kwargs:
        :return:
        """
        pass

    @abc.abstractmethod
    def type_counts_query(
            self,
            search_term,
            type_filters: List[str]=None,
            **kwargs):
        """
        ONS aggregations query to compute _type counts
        :param search_term:
        :param type_filters:
        :param kwargs:
        :return:
        """
        pass

    @abc.abstractmethod
    def featured_result_query(self, search_term):
        """
        ONS query for featured pages
        :param search_term:
        :return:
        """
        pass


class SearchEngine(AbstractSearchClient):
    """
    Default ONS search client.
    """

    def departments_query(
            self,
            search_term: str,
            current_page: int,
            size: int):
        """
        Executes the ONS departments query
        :param search_term:
        :param current_page:
        :param size:
        :return:
        """
        from ons.search.queries import departments_query

        query = departments_query(search_term)
        query_dict = {
            "query": query.to_dict()
        }

        self.update_from_dict(query_dict)

        s: SearchEngine = self._clone()

        # Set search_type and highlight options
        s: SearchEngine = s.search_type(SearchType.DFS_QUERY_THEN_FETCH)
        s: SearchEngine = s.highlight(
            "terms",
            fragment_size=0,
            pre_tags=["<strong>"],
            post_tags=["</strong>"])

        # Calculate from_start param
        from_start = 0 if current_page <= 1 else (current_page - 1) * size
        end = from_start + size

        # Setup pagination
        s: SearchEngine = s[from_start:end]

        return s

    def content_query(
            self,
            search_term: str,
            current_page: int = 1,
            size: int = 10,
            **kwargs):
        """
        Implementation of default ONS content query
        :param search_term:
        :param current_page:
        :param size:
        :param kwargs:
        :return:
        """
        from ons.search.filter_functions import content_filter_functions
        from ons.search.queries import content_query, function_score_content_query

        # Build the standard content query
        query = content_query(search_term)

        function_scores = kwargs.get(
            "function_scores", content_filter_functions())

        if function_scores is not None:
            query = function_score_content_query(
                query,
                function_scores)

        return self.build(
            query,
            current_page=current_page,
            size=size,
            **kwargs)

    def type_counts_query(
            self,
            search_term,
            type_filters: List[str]=None,
            **kwargs):
        from ons.search.queries import type_counts_query

        if type_filters is None:
            from ons.search.type_filter import default_filters
            type_filters = default_filters()

        # Prepare and execute
        return self.content_query(
            search_term,
            function_scores=None,
            aggs=type_counts_query,
            type_filters=type_filters,
            **kwargs)

    def featured_result_query(self, search_term):
        """
        Builds and executes the standard ONS featured result query (from babbage)
        :param search_term:
        :return:
        """
        from ons.search.content_type import home_page_census, product_page

        type_filters = [product_page.name, home_page_census.name]

        return self.content_query(
            search_term,
            function_scores=None,
            type_filters=type_filters,
            size=1)
